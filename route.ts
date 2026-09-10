import { NextResponse } from "next/server";

export async function GET(_: Request, context: { params: Promise<{ code: string }> }) {
  const { code } = await context.params;
  if (!/^\d{6}$/.test(code)) return NextResponse.json({ error: "invalid fund code" }, { status: 400 });

  // MVP adapter. Replace/extend this provider with a licensed/stable fund-data source.
  // The frontend talks only to this route, so the provider can change later without UI changes.
  return NextResponse.json({
    code,
    provider: "placeholder",
    message: "基金数据 Provider 尚未接入。下一阶段在此接入稳定的中国基金净值 API。",
  });
}