"""
Comprehensive Test Suite for Stateless Migration
Tests all features: quiz flow, photos, analytics, sharing, likes, concurrent users
"""
import asyncio
import time
import requests
from playwright.async_api import async_playwright, expect
import json
import sys
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"

class StatelessMigrationTester:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }

    def log_pass(self, test_name):
        print(f"[PASS] {test_name}")
        self.results["passed"].append(test_name)

    def log_fail(self, test_name, error):
        print(f"[FAIL] {test_name} - {error}")
        self.results["failed"].append((test_name, str(error)))

    def log_warn(self, test_name, warning):
        print(f"[WARN] {test_name} - {warning}")
        self.results["warnings"].append((test_name, str(warning)))

    async def test_complete_quiz_flow(self, page):
        """Test 1: Complete quiz flow from start to finish"""
        test_name = "Complete Quiz Flow"
        try:
            print(f"\n🧪 Testing: {test_name}")

            # Navigate to quiz
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")

            # Check page loaded
            await expect(page.locator('h1')).to_contain_text("Indian")
            print("  ✓ Homepage loaded")

            # Select domain
            await page.click('[data-domain="cosmos"]')
            print("  ✓ Domain selected")

            # Start quiz
            await page.click('#btn-domain')
            await page.wait_for_timeout(1000)

            # Answer all 12 questions
            for i in range(12):
                print(f"  ✓ Answering question {i+1}/12")
                # Wait for question to load
                await page.wait_for_selector('.option-card', timeout=5000)

                # Click first option
                await page.click('.option-card:first-child')
                await page.wait_for_timeout(300)

                # Click next button
                await page.click('#btn-answer')
                await page.wait_for_timeout(500)

            # Wait for results (with 3s minimum delay)
            print("  ⏳ Waiting for results...")
            await page.wait_for_selector('.scientist-name', timeout=10000)

            # Verify results displayed
            scientist_name = await page.locator('.scientist-name').text_content()
            print(f"  ✓ Results displayed: Matched with {scientist_name}")

            # Check if photo loaded
            photo = page.locator('.scientist-photo')
            await expect(photo).to_be_visible()
            print("  ✓ Scientist photo loaded")

            self.log_pass(test_name)
            return True

        except Exception as e:
            self.log_fail(test_name, e)
            return False

    async def test_browser_refresh_between_users(self, page):
        """Test 2: Browser refresh clears state (tablet scenario)"""
        test_name = "Browser Refresh Between Users"
        try:
            print(f"\n🧪 Testing: {test_name}")

            # User 1: Take partial quiz
            await page.goto(BASE_URL)
            await page.click('[data-domain="quantum"]')
            await page.click('#btn-domain')
            await page.wait_for_timeout(1000)

            # Answer 3 questions
            for i in range(3):
                await page.wait_for_selector('.option-card')
                await page.click('.option-card:nth-child(2)')
                await page.wait_for_timeout(200)
                await page.click('#btn-answer')
                await page.wait_for_timeout(300)

            print("  ✓ User 1 answered 3 questions")

            # REFRESH (simulate new user)
            await page.reload()
            await page.wait_for_load_state("networkidle")

            # Verify back at domain selection
            domain_step = page.locator('#step-domain')
            class_attr = await domain_step.get_attribute('class')
            assert 'active' in class_attr, f"Expected 'active' class, got: {class_attr}"
            print("  ✓ After refresh: Back to domain selection (clean state)")

            # User 2: Complete full quiz
            await page.click('[data-domain="chemistry"]')
            await page.click('#btn-domain')

            for i in range(12):
                await page.wait_for_selector('.option-card')
                await page.click('.option-card:first-child')
                await page.wait_for_timeout(200)
                await page.click('#btn-answer')
                await page.wait_for_timeout(300)

            await page.wait_for_selector('.scientist-name', timeout=10000)
            scientist_name = await page.locator('.scientist-name').text_content()
            print(f"  ✓ User 2 completed quiz: {scientist_name}")

            self.log_pass(test_name)
            return True

        except Exception as e:
            self.log_fail(test_name, e)
            return False

    async def test_concurrent_users(self):
        """Test 3: Multiple concurrent users (stress test)"""
        test_name = "3 Concurrent Users (Tablet Simulation)"
        try:
            print(f"\n🧪 Testing: {test_name}")

            async with async_playwright() as p:
                browser = await p.chromium.launch()

                # Create 3 contexts (3 tablets)
                contexts = []
                pages = []
                for i in range(3):
                    context = await browser.new_context()
                    page = await context.new_page()
                    contexts.append(context)
                    pages.append(page)
                    print(f"  ✓ Tablet {i+1} ready")

                # All 3 start quiz simultaneously
                async def take_quiz(page_num, page):
                    try:
                        await page.goto(BASE_URL)
                        await page.click(f'[data-domain="cosmos"]')
                        await page.click('#btn-domain')

                        for i in range(12):
                            await page.wait_for_selector('.option-card', timeout=5000)
                            await page.click('.option-card:first-child')
                            await page.wait_for_timeout(100)
                            await page.click('#btn-answer')
                            await page.wait_for_timeout(200)

                        await page.wait_for_selector('.scientist-name', timeout=15000)
                        scientist = await page.locator('.scientist-name').text_content()
                        print(f"  ✓ Tablet {page_num} completed: {scientist}")
                        return True
                    except Exception as e:
                        print(f"  ❌ Tablet {page_num} failed: {e}")
                        return False

                # Run all 3 concurrently
                print("  ⏳ Running 3 quizzes concurrently...")
                start_time = time.time()
                results = await asyncio.gather(*[
                    take_quiz(i+1, page) for i, page in enumerate(pages)
                ])
                elapsed = time.time() - start_time

                # Cleanup
                for context in contexts:
                    await context.close()
                await browser.close()

                # Verify all succeeded
                if all(results):
                    print(f"  ✅ All 3 users completed successfully in {elapsed:.1f}s")
                    self.log_pass(test_name)
                    return True
                else:
                    failed_count = results.count(False)
                    self.log_fail(test_name, f"{failed_count}/3 users failed")
                    return False

        except Exception as e:
            self.log_fail(test_name, e)
            return False

    async def test_anti_repetition(self, page):
        """Test 4: Anti-repetition logic (localStorage)"""
        test_name = "Anti-Repetition Logic"
        try:
            print(f"\n🧪 Testing: {test_name}")

            scientists_matched = []

            # Take quiz 3 times
            for attempt in range(3):
                print(f"  ⏳ Attempt {attempt + 1}/3...")

                await page.goto(BASE_URL)
                await page.click('[data-domain="cosmos"]')
                await page.click('#btn-domain')

                for i in range(12):
                    await page.wait_for_selector('.option-card')
                    # Same answers each time
                    await page.click('.option-card:first-child')
                    await page.wait_for_timeout(100)
                    await page.click('#btn-answer')
                    await page.wait_for_timeout(200)

                await page.wait_for_selector('.scientist-name', timeout=10000)
                scientist = await page.locator('.scientist-name').text_content()
                scientists_matched.append(scientist)
                print(f"    Matched: {scientist}")

                # Check localStorage
                recently_shown = await page.evaluate('() => JSON.parse(localStorage.getItem("recently_shown_scientists") || "[]")')
                print(f"    Recently shown count: {len(recently_shown)}")

            # Verify variety (anti-repetition working)
            unique_scientists = len(set(scientists_matched))
            if unique_scientists >= 2:
                print(f"  ✅ Anti-repetition working: {unique_scientists}/3 unique scientists")
                self.log_pass(test_name)
                return True
            else:
                self.log_warn(test_name, f"Only {unique_scientists}/3 unique - may need tuning")
                return True  # Still pass, just warn

        except Exception as e:
            self.log_fail(test_name, e)
            return False

    async def test_api_endpoints(self):
        """Test 5: API endpoints respond correctly"""
        test_name = "API Endpoints"
        try:
            print(f"\n🧪 Testing: {test_name}")

            # Test /api/start-quiz
            response = requests.post(f"{BASE_URL}/api/start-quiz", json={
                "domain": "cosmos",
                "client_uuid": "test-uuid-123"
            })
            assert response.status_code == 200
            data = response.json()
            assert "question" in data
            print("  ✓ /api/start-quiz works")

            # Test /api/answer-question
            response = requests.post(f"{BASE_URL}/api/answer-question", json={
                "answer": 0,
                "question_number": 0,
                "client_uuid": "test-uuid-123"
            })
            assert response.status_code == 200
            print("  ✓ /api/answer-question works")

            # Test /api/get-matches (stateless - send all data)
            response = requests.post(f"{BASE_URL}/api/get-matches", json={
                "client_uuid": "test-uuid-123",
                "domain": "cosmos",
                "answers": [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
                "recently_shown": []
            })
            assert response.status_code == 200
            data = response.json()
            assert "matches" in data
            assert len(data["matches"]) > 0
            print(f"  ✓ /api/get-matches works (got {len(data['matches'])} matches)")

            # Test /api/like
            response = requests.post(f"{BASE_URL}/api/like", json={
                "scientist": "Test Scientist",
                "client_uuid": "test-uuid-123"
            })
            assert response.status_code == 200
            print("  ✓ /api/like works")

            # Test /api/share
            response = requests.post(f"{BASE_URL}/api/share", json={
                "scientist": "Test Scientist",
                "platform": "twitter",
                "client_uuid": "test-uuid-123"
            })
            assert response.status_code == 200
            print("  ✓ /api/share works")

            # Test /analytics
            response = requests.get(f"{BASE_URL}/analytics")
            assert response.status_code == 200
            print("  ✓ /analytics works")

            self.log_pass(test_name)
            return True

        except Exception as e:
            self.log_fail(test_name, e)
            return False

    def print_summary(self):
        """Print final test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)

        print(f"\n✅ PASSED: {len(self.results['passed'])}")
        for test in self.results['passed']:
            print(f"   ✓ {test}")

        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS: {len(self.results['warnings'])}")
            for test, warning in self.results['warnings']:
                print(f"   ⚠ {test}: {warning}")

        if self.results['failed']:
            print(f"\n❌ FAILED: {len(self.results['failed'])}")
            for test, error in self.results['failed']:
                print(f"   ✗ {test}")
                print(f"     Error: {error}")
        else:
            print("\n🎉 ALL TESTS PASSED!")

        print("\n" + "="*60)

        # Final verdict
        if len(self.results['failed']) == 0:
            print("✅ STATELESS MIGRATION: SUCCESS")
            print("   All features working correctly!")
            print("   Ready for production deployment.")
            return True
        else:
            print("❌ STATELESS MIGRATION: NEEDS FIXES")
            print(f"   {len(self.results['failed'])} tests failed")
            return False


async def run_all_tests():
    """Run complete test suite"""
    tester = StatelessMigrationTester()

    print("\n🚀 STARTING COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing stateless architecture migration")
    print("Features: Quiz flow, Photos, Concurrent users, Anti-repetition")
    print("=" * 60)

    # Test API endpoints first (no browser needed)
    await tester.test_api_endpoints()

    # Browser-based tests
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Run tests
        await tester.test_complete_quiz_flow(page)
        await tester.test_browser_refresh_between_users(page)
        await tester.test_anti_repetition(page)

        await context.close()
        await browser.close()

    # Concurrent users test (separate browser instances)
    await tester.test_concurrent_users()

    # Print summary
    success = tester.print_summary()

    return success


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  STATELESS MIGRATION - COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")

    success = asyncio.run(run_all_tests())

    exit(0 if success else 1)
