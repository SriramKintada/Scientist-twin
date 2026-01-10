"""
FINAL VERIFICATION - What actually happens at scale?
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

async def test_single_full_quiz():
    """Test one complete quiz"""
    print("\n[TEST 1] Single user - Full 12-question quiz")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            start = time.time()
            await page.goto(PRODUCTION_URL, timeout=30000)
            await page.wait_for_load_state("domcontentloaded", timeout=20000)
            await asyncio.sleep(3)

            frames = page.frames
            quiz_frame = frames[1] if len(frames) > 1 else page

            # Start quiz
            await quiz_frame.wait_for_selector('[data-domain]', timeout=15000)
            await quiz_frame.click('[data-domain="cosmos"]')
            await asyncio.sleep(0.3)
            await quiz_frame.click('#btn-domain')
            await asyncio.sleep(0.5)

            # Answer all 12 questions
            for i in range(12):
                await quiz_frame.wait_for_selector('.option-card', timeout=12000)
                await quiz_frame.click('.option-card:first-child')
                await asyncio.sleep(0.5)
                await quiz_frame.wait_for_selector('#btn-answer:not([disabled])', timeout=10000)
                await quiz_frame.click('#btn-answer')
                await asyncio.sleep(0.5)

            # Wait for results
            await quiz_frame.wait_for_selector('.scientist-name', timeout=30000)
            scientist = await quiz_frame.locator('.scientist-name').text_content()

            elapsed = time.time() - start
            await context.close()
            await browser.close()

            print(f"  SUCCESS: Matched with {scientist} in {elapsed:.1f}s")
            return True

        except Exception as e:
            print(f"  FAILED: {str(e)[:150]}")
            try:
                await context.close()
                await browser.close()
            except:
                pass
            return False

async def test_sequential_burst(num_users, start_num=1):
    """Test N sequential users quickly"""
    print(f"\n[TEST] Sequential burst: Users {start_num} to {start_num + num_users - 1}")

    successful = 0
    failed = 0
    errors = []
    start_time = time.time()

    for i in range(num_users):
        user_num = start_num + i

        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(PRODUCTION_URL, timeout=30000)
                await page.wait_for_load_state("domcontentloaded", timeout=20000)
                await asyncio.sleep(2)

                frames = page.frames
                quiz_frame = frames[1] if len(frames) > 1 else page

                # Quick quiz - just 3 questions
                await quiz_frame.wait_for_selector('[data-domain]', timeout=15000)
                await quiz_frame.click('[data-domain="cosmos"]')
                await asyncio.sleep(0.3)
                await quiz_frame.click('#btn-domain')
                await asyncio.sleep(0.5)

                for j in range(3):
                    await quiz_frame.wait_for_selector('.option-card', timeout=12000)
                    await quiz_frame.click('.option-card:first-child')
                    await asyncio.sleep(0.5)
                    await quiz_frame.wait_for_selector('#btn-answer:not([disabled])', timeout=10000)
                    await quiz_frame.click('#btn-answer')
                    await asyncio.sleep(0.5)

                await context.close()
                await browser.close()
                successful += 1

            except Exception as e:
                error = str(e)[:100]
                errors.append((user_num, error))
                failed += 1
                try:
                    await context.close()
                    await browser.close()
                except:
                    pass

    elapsed = time.time() - start_time
    rate = num_users / elapsed * 60

    print(f"  Result: {successful}/{num_users} OK, {failed} failed in {elapsed:.1f}s ({rate:.1f}/min)")

    if errors:
        print(f"  Errors:")
        for user_num, error in errors[:5]:
            print(f"    User {user_num}: {error}")

    return successful, failed, errors

async def main():
    print("="*70)
    print("  FINAL VERIFICATION TEST")
    print(f"  URL: {PRODUCTION_URL}")
    print("="*70)

    # Test 1: Single full quiz
    result1 = await test_single_full_quiz()
    if not result1:
        print("\n❌ BASIC TEST FAILED - STOPPING")
        return False

    # Test 2: First 20 users
    success_20, fail_20, errors_20 = await test_sequential_burst(20, start_num=1)

    # Test 3: Users 21-40
    success_40, fail_40, errors_40 = await test_sequential_burst(20, start_num=21)

    # Test 4: Users 41-60 (where problems might start)
    success_60, fail_60, errors_60 = await test_sequential_burst(20, start_num=41)

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"  Users 1-20:   {success_20}/20 OK ({fail_20} failed)")
    print(f"  Users 21-40:  {success_40}/20 OK ({fail_40} failed)")
    print(f"  Users 41-60:  {success_60}/20 OK ({fail_60} failed)")

    total_success = success_20 + success_40 + success_60
    total_fail = fail_20 + fail_40 + fail_60
    success_rate = (total_success / 60) * 100

    print(f"\n  Overall: {total_success}/60 ({success_rate:.0f}% success rate)")

    if errors_60:
        print(f"\n  Issues found in users 41-60:")
        for user_num, error in errors_60[:3]:
            print(f"    User {user_num}: {error}")

    if success_rate >= 95:
        print("\n✅ APP READY FOR TOMORROW'S EVENT")
        return True
    elif success_rate >= 80:
        print("\n⚠️  APP WORKS BUT WITH SOME ISSUES")
        return True
    else:
        print("\n❌ APP HAS SERIOUS PROBLEMS")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
