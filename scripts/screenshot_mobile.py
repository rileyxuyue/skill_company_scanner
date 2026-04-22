#!/usr/bin/env python3
"""Mobile-optimized screenshot script for page-wrap style reports.
Usage: python3 screenshot_mobile.py <html_path> <output_dir>
"""
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image

MOBILE_VP = {"width": 420, "height": 900}
SCALE = 3
GIF_FRAMES = 40
GIF_MS = 125

async def main(html_path, output_dir):
    url = f"file://{os.path.abspath(html_path)}"
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport=MOBILE_VP, device_scale_factor=SCALE)
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Collect all .sec elements
        secs = await page.query_selector_all(".sec")
        hero = await page.query_selector("header.hero")
        footer = await page.query_selector("footer.footer")

        names = [
            "00_hero",
            "01_summary", "02_business", "03_moat", "04_upside",
            "05_downside", "06_revenue", "07_finance", "08_team",
            "09_investors", "10_scale", "11_culture", "12_jobs",
            "13_footer"
        ]

        # Hero
        if hero:
            await hero.screenshot(path=os.path.join(output_dir, "00_hero.png"), timeout=60000)
            print("  ✅ 00_hero.png")

        # Sections
        for i, sec in enumerate(secs):
            name = names[i + 1] if i + 1 < len(names) else f"{i+1:02d}_section"
            path = os.path.join(output_dir, f"{name}.png")
            await sec.screenshot(path=path, timeout=60000)
            print(f"  ✅ {name}.png")

        # Footer
        if footer:
            await footer.screenshot(path=os.path.join(output_dir, "13_footer.png"), timeout=60000)
            print("  ✅ 13_footer.png")

        # Hero GIF
        print("  🎬 Recording Hero GIF...")
        if hero:
            frames = []
            for i in range(GIF_FRAMES):
                fp = os.path.join(output_dir, f"_f{i:03d}.png")
                await hero.screenshot(path=fp, timeout=60000)
                frames.append(fp)
                await page.wait_for_timeout(GIF_MS)

            imgs = []
            for f in frames:
                img = Image.open(f).convert("RGBA")
                w, h = img.size
                nw = min(w, 1260)
                nh = int(h * nw / w)
                img = img.resize((nw, nh), Image.LANCZOS)
                imgs.append(img.convert("P", palette=Image.ADAPTIVE, colors=160))

            gif_path = os.path.join(output_dir, "00_hero_animated.gif")
            imgs[0].save(gif_path, save_all=True, append_images=imgs[1:],
                         duration=GIF_MS, loop=0, optimize=True)
            mb = os.path.getsize(gif_path) / 1024 / 1024
            print(f"  ✅ 00_hero_animated.gif ({mb:.1f}MB)")

            for f in frames:
                os.remove(f)

        await browser.close()
        print(f"\n🎉 Done! → {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 screenshot_mobile.py <html_path> <output_dir>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
