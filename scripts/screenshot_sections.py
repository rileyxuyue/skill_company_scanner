#!/usr/bin/env python3
"""
公司扫描报告截图脚本
用法: python3 screenshot_sections.py <html_file_path> <output_dir>

输出两套截图：
1. 桌面版（viewport 1080px, 3x）—— 每个section单独截图 + Hero动画GIF
2. 手机版（viewport 390px, 3x, 9:16）—— 每个section适配手机长图 + Hero动画GIF
"""
import asyncio
import sys
import os
from playwright.async_api import async_playwright
from PIL import Image

DESKTOP_VP = {"width": 600, "height": 1080}
MOBILE_VP = {"width": 390, "height": 844}
SCALE = 3
GIF_FRAMES = 40
GIF_INTERVAL_MS = 125  # 125ms * 40 = 5s cycle

SECTIONS = [
    {"name": "00_hero", "selector": "header.hero"},
    {"name": "01_summary", "selector": ".sec:nth-of-type(1)"},
    {"name": "02_business", "selector": ".sec:nth-of-type(2)"},
    {"name": "03_moat", "selector": ".sec:nth-of-type(3)"},
    {"name": "04_upside", "selector": ".sec:nth-of-type(4)"},
    {"name": "05_downside", "selector": ".sec:nth-of-type(5)"},
    {"name": "06_revenue", "selector": ".sec:nth-of-type(6)"},
    {"name": "07_finance", "selector": ".sec:nth-of-type(7)"},
    {"name": "08_team", "selector": ".sec:nth-of-type(8)"},
    {"name": "09_investors", "selector": ".sec:nth-of-type(9)"},
    {"name": "10_scale", "selector": ".sec:nth-of-type(10)"},
    {"name": "11_culture", "selector": ".sec:nth-of-type(11)"},
    {"name": "12_jobs", "selector": ".sec:nth-of-type(12)"},
    {"name": "13_footer", "selector": "footer.footer"},
]


async def screenshot_desktop(page, output_dir):
    """桌面版：每个section截图 + Hero GIF"""
    desk_dir = os.path.join(output_dir, "desktop")
    os.makedirs(desk_dir, exist_ok=True)

    for sec in SECTIONS:
        el = await page.query_selector(sec["selector"])
        if el:
            path = os.path.join(desk_dir, f"{sec['name']}.png")
            await el.screenshot(path=path, timeout=60000)
            print(f"  ✅ desktop/{sec['name']}.png")
        else:
            print(f"  ❌ desktop/{sec['name']} — not found: {sec['selector']}")

    # Hero GIF
    print("  🎬 Recording desktop Hero GIF...")
    hero = await page.query_selector("header.hero")
    if hero:
        frames = []
        for i in range(GIF_FRAMES):
            fp = os.path.join(desk_dir, f"_frame_{i:03d}.png")
            await hero.screenshot(path=fp)
            frames.append(fp)
            await page.wait_for_timeout(GIF_INTERVAL_MS)

        imgs = [Image.open(f) for f in frames]
        # Compress: reduce colors
        compressed = []
        for img in imgs:
            img = img.convert("RGBA")
            w, h = img.size
            new_w = min(w, 1080)
            ratio = new_w / w
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            compressed.append(img.convert("P", palette=Image.ADAPTIVE, colors=128))

        gif_path = os.path.join(desk_dir, "00_hero_animated.gif")
        compressed[0].save(gif_path, save_all=True, append_images=compressed[1:],
                           duration=GIF_INTERVAL_MS, loop=0, optimize=True)
        print(f"  ✅ desktop/00_hero_animated.gif ({os.path.getsize(gif_path)/1024/1024:.1f}MB)")

        for f in frames:
            os.remove(f)


async def screenshot_mobile(page, output_dir):
    """手机版：每个section截图（适配竖屏）+ Hero 9:16 GIF"""
    mob_dir = os.path.join(output_dir, "mobile")
    os.makedirs(mob_dir, exist_ok=True)

    for sec in SECTIONS:
        el = await page.query_selector(sec["selector"])
        if el:
            path = os.path.join(mob_dir, f"{sec['name']}.png")
            await el.screenshot(path=path, timeout=60000)
            print(f"  ✅ mobile/{sec['name']}.png")
        else:
            print(f"  ❌ mobile/{sec['name']} — not found: {sec['selector']}")

    # Hero 9:16 GIF
    print("  🎬 Recording mobile Hero GIF (9:16)...")
    TARGET_W, TARGET_H = 1080, 1920
    frames = []
    for i in range(GIF_FRAMES):
        fp = os.path.join(mob_dir, f"_mframe_{i:03d}.png")
        await page.screenshot(path=fp, clip={"x": 0, "y": 0, "width": 390, "height": 693})
        frames.append(fp)
        await page.wait_for_timeout(GIF_INTERVAL_MS)

    imgs = []
    for f in frames:
        img = Image.open(f).convert("RGBA").resize((TARGET_W, TARGET_H), Image.LANCZOS)
        imgs.append(img.convert("P", palette=Image.ADAPTIVE, colors=192))

    gif_path = os.path.join(mob_dir, "00_hero_animated.gif")
    imgs[0].save(gif_path, save_all=True, append_images=imgs[1:],
                 duration=GIF_INTERVAL_MS, loop=0, optimize=True)
    print(f"  ✅ mobile/00_hero_animated.gif ({os.path.getsize(gif_path)/1024/1024:.1f}MB)")

    # Static mobile hero PNG
    static = Image.open(frames[0]).resize((TARGET_W, TARGET_H), Image.LANCZOS)
    static.save(os.path.join(mob_dir, "00_hero_mobile.png"))
    print(f"  ✅ mobile/00_hero_mobile.png")

    for f in frames:
        os.remove(f)


async def main(html_path, output_dir):
    url = f"file://{os.path.abspath(html_path)}"
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Desktop screenshots
        print("\n📸 Desktop screenshots (1080px viewport, 3x)...")
        page_d = await browser.new_page(viewport=DESKTOP_VP, device_scale_factor=SCALE)
        await page_d.goto(url, wait_until="networkidle")
        await page_d.wait_for_timeout(2000)
        await screenshot_desktop(page_d, output_dir)
        await page_d.close()

        # Mobile screenshots
        print("\n📱 Mobile screenshots (390px viewport, 3x)...")
        page_m = await browser.new_page(viewport=MOBILE_VP, device_scale_factor=SCALE)
        await page_m.goto(url, wait_until="networkidle")
        await page_m.wait_for_timeout(2000)
        await screenshot_mobile(page_m, output_dir)
        await page_m.close()

        await browser.close()

    print(f"\n🎉 All done! Screenshots saved to: {output_dir}")
    print(f"   desktop/ — 网页原始尺寸截图 + Hero动画GIF")
    print(f"   mobile/  — 手机适配截图 + 9:16 Hero动画GIF")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 screenshot_sections.py <html_file_path> <output_dir>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
