import html
import ipaddress
import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx
import trafilatura
from fastapi import HTTPException

from app.core.config import Settings
from app.schemas.experience import ExperienceSearchResultItem, ExperienceSearchWebRequest, ExperienceSearchWebResponse


RESULT_PATTERN = re.compile(
    r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?(?:class="result__snippet"[^>]*>(?P<snippet_a>.*?)</a>|class="result__snippet"[^>]*>(?P<snippet_div>.*?)</div>)',
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_STYLE_PATTERN = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


class ExperienceSearchService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, payload: ExperienceSearchWebRequest) -> ExperienceSearchWebResponse:
        provider = self.settings.search_provider.lower().strip()
        if not any([payload.keyword, payload.target_school, payload.target_major]):
            raise HTTPException(status_code=422, detail="Please provide at least one of keyword, target_school, or target_major")
        if provider != "duckduckgo_html":
            raise HTTPException(status_code=501, detail=f"Search provider '{provider}' is not supported yet")

        query = self._build_query(payload)
        max_results = min(payload.max_results, self.settings.search_max_results)
        results = await self._search_duckduckgo_html(query, max_results)
        return ExperienceSearchWebResponse(
            provider="duckduckgo_html",
            query_used=query,
            message=None if results else "未检索到足够相关的面经结果，请调整学校、专业或关键词后重试。",
            results=results,
        )

    async def _search_duckduckgo_html(self, query: str, max_results: int) -> list[ExperienceSearchResultItem]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://duckduckgo.com/",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0, headers=headers, follow_redirects=True) as client:
                response = await client.post(self.settings.duckduckgo_html_url, data={"q": query})
                response.raise_for_status()
                parsed = self._parse_duckduckgo_results(response.text)
                results = []
                for item in parsed[:max_results]:
                    raw_content = await self._fetch_page_text(client, item["url"], item["snippet"])
                    results.append(
                        ExperienceSearchResultItem(
                            title=item["title"],
                            url=item["url"],
                            source_site=self._extract_source_site(item["url"]),
                            snippet=self._trim_text(item["snippet"], limit=600),
                            raw_content=self._trim_text(raw_content, limit=12000),
                            published_date=None,
                            score=None,
                        )
                    )
                return results
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=502, detail=f"Search provider request failed: {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Search provider is temporarily unavailable") from exc

    def _parse_duckduckgo_results(self, search_html: str) -> list[dict]:
        results: list[dict] = []
        seen_urls: set[str] = set()
        for match in RESULT_PATTERN.finditer(search_html):
            raw_href = match.group("href")
            url = self._normalize_result_url(raw_href)
            title = self._clean_html_text(match.group("title"))
            snippet = self._clean_html_text(match.group("snippet_a") or match.group("snippet_div") or "")
            if not url or not title or url in seen_urls:
                continue
            if not self._is_allowed_url(url):
                continue
            seen_urls.add(url)
            results.append({"title": title, "url": url, "snippet": snippet})
        return results

    async def _fetch_page_text(self, client: httpx.AsyncClient, url: str, snippet: str) -> str:
        if not self._is_allowed_url(url):
            return self._trim_text(snippet, limit=12000)
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            return self._trim_text(snippet, limit=12000)
        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            return self._trim_text(snippet, limit=12000)

        page_html = response.text
        extracted_text = self._extract_main_content(page_html, url)
        if extracted_text:
            return self._trim_text(extracted_text, limit=20000)

        cleaned_text = self._fallback_clean_text(page_html)
        if cleaned_text:
            return self._trim_text(cleaned_text, limit=20000)

        return self._trim_text(snippet, limit=12000)

    def _build_query(self, payload: ExperienceSearchWebRequest) -> str:
        parts = [payload.keyword or ""]
        metadata_parts = [
            payload.target_school,
            payload.target_major,
            payload.target_lab,
            payload.target_teacher,
            payload.interview_type,
            str(payload.year) if payload.year else None,
        ]
        parts.extend([part for part in metadata_parts if part])
        parts.extend(["保研", "推免", "复试", "面经"])
        seen = set()
        ordered_parts = []
        for part in parts:
            normalized = part.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered_parts.append(normalized)
        return " ".join(ordered_parts)

    def _normalize_result_url(self, raw_href: str) -> str | None:
        href = html.unescape(raw_href or "").strip()
        if not href:
            return None
        if href.startswith("//"):
            href = f"https:{href}"
        parsed = urlparse(href)
        if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
            uddg = parse_qs(parsed.query).get("uddg", [])
            if uddg:
                return unquote(uddg[0])
        return href

    @staticmethod
    def _extract_source_site(source_url: str | None) -> str | None:
        if not source_url:
            return None
        try:
            parsed = urlparse(source_url)
            return parsed.netloc or None
        except Exception:
            return None

    @staticmethod
    def _clean_html_text(text: str) -> str:
        without_tags = TAG_PATTERN.sub(" ", text)
        return WHITESPACE_PATTERN.sub(" ", html.unescape(without_tags)).strip()

    @staticmethod
    def _extract_main_content(page_html: str, url: str) -> str:
        try:
            extracted = trafilatura.extract(
                page_html,
                url=url,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
                deduplicate=True,
            )
            return (extracted or "").strip()
        except Exception:
            return ""

    @staticmethod
    def _fallback_clean_text(page_html: str) -> str:
        body = SCRIPT_STYLE_PATTERN.sub(" ", page_html)
        body = TAG_PATTERN.sub(" ", body)
        return WHITESPACE_PATTERN.sub(" ", html.unescape(body)).strip()

    @staticmethod
    def _trim_text(text: str, limit: int = 4000) -> str:
        normalized = WHITESPACE_PATTERN.sub(" ", text).strip()
        return normalized[:limit]

    @staticmethod
    def _is_allowed_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        if parsed.scheme not in {"http", "https"}:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            return not (ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local)
        except ValueError:
            return True
