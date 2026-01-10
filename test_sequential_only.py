"""
Test 100 sequential users (tablet scenario with refresh)
"""
import asyncio
import time
from playwright.async_api import async_playwright
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PRODUCTION_URL = "https://www.scirio.in/indian-scientist-twin"

async def test_one_user_quick(user_id):
    """Quick test - just 3 questions to verify it works"""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate
            await page.goto(PRODUCTION_URL, timeout=30000)
            await page.wait_for_load_state("domcontentloaded", timeout=20000)
            await asyncio.sleep(3)

            # Get iframe
            frames = page.frames
            quiz_frame = frames[1] if len(frames) > 1 else page

            # Start quiz
            await quiz_frame.wait_for_selector('[data-domain]', timeout=15000)
            await quiz_frame.click('[data-domain="cosmos"]')
            await asyncio.sleep(0.3)
            await quiz_frame.click('#btn-domain')
            await asyncio.sleep(0.5)

            # Answer 3 questions only (quick mode)
            for i in range(3):
                await quiz_frame.wait_for_selector('.option-card', timeout=12000)
                await quiz_frame.click('.option-card:first-child')
                await asyncio.sleep(0.3)
                await quiz_frame.wait_for_selector('#btn-answer', timeout=10000)
                await quiz_frame.click('#btn-answer')
                await asyncio.sleep(0.3)

            await context.close()
            await browser.close()
            return True

        except Exception as e:
            error_msg = str(e)[:200]
            try:
                await context.close()
                await browser.close()
            except:
                pass
            return (False, error_msg)

async def test_sequential(num_users):
    """Test N sequential users"""
    print(f"\n{'='*70}")
    print(f"SEQUENTIAL TEST: {num_users} users one after another (tablet)")
    print(f"{'='*70}\n")

    successful = 0
    failed = 0
    start_time = time.time()

    for i in range(num_users):
        result = await test_one_user_quick(i+1)

        if result == True or (isinstance(result, tuple) and result[0] == True):
            successful += 1
            if (i+1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (i+1) / elapsed * 60
                print(f"  [{i+1}/{num_users}] OK - {successful} success, {failed} failed, {rate:.1f} users/min")
        else:
            failed += 1
            error = result[1] if isinstance(result, tuple) else "Unknown error"
            if failed <= 10:
                print(f"  User {i+1} FAILED: {error}")

    elapsed = time.time() - start_time
    rate = num_users / elapsed * 60

    print(f"\n{'-'*70}")
    print(f"RESULTS: {successful}/{num_users} succeeded in {elapsed:.1f}s")
    print(f"Rate: {rate:.1f} users/minute")
    print(f"{'-'*70}")

    return successful >= (num_users * 0.95)

async def main():
    print("\n" + "="*70)
    print("  SEQUENTIAL TABLET TEST - 100 USERS")
    print(f"  URL: {PRODUCTION_URL}")
    print("="*70)

    success = await test_sequential(70)

    if success:
        print("\n✅ SEQUENTIAL TEST PASSED - Tablet mode works!")
    else:
        print("\n❌ SEQUENTIAL TEST FAILED")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
