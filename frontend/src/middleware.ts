import createMiddleware from "next-intl/middleware";
import { NextRequest, NextResponse } from "next/server";

const intlMiddleware = createMiddleware({
  locales: ["en", "es"],
  defaultLocale: "es",
});

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("auth_token")?.value;

  // Paths that are public (login, etc)
  const isPublicPage =
    pathname.includes("/login") ||
    pathname.includes("/register") ||
    pathname === "/" ||
    pathname === "/en" ||
    pathname === "/es";

  // If not a public page and no token, redirect to login
  if (!isPublicPage && !token) {
    const locale = pathname.startsWith("/en") ? "en" : "es";
    return NextResponse.redirect(new URL(`/${locale}/login`, request.url));
  }

  // If already logged in and going to login, redirect to dashboard (/)
  if (isPublicPage && token && pathname.includes("/login")) {
    const locale = pathname.startsWith("/en") ? "en" : "es";
    return NextResponse.redirect(new URL(`/${locale}/`, request.url));
  }

  return intlMiddleware(request);
}

export const config = {
  // Match only internationalized pathnames
  matcher: ["/", "/(es|en)/:path*"],
};
