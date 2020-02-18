# Testing
from bm import bufferManager, clock, BufferPoolFullError
from dm import diskManager
from page import page
from frame import frame
import sys


class testingBM:

    def test1(self):

        print("====== TEST 1 ======")
        print("this only tests the clock algorithm, buffer management features (pin and unpin) are not tested.")
        status = True

        print("1) Creating a smaple buffer of five frames\n")
        buf = []
        for i in range(5):
            buf.append(frame())

        buf[0].pinCount = 1
        buf[0].referenced = 1
        buf[0].frameNumber = 0

        buf[1].pinCount = 0
        buf[1].referenced = 1
        buf[1].frameNumber = 1

        buf[2].pinCount = 1
        buf[2].referenced = 1
        buf[2].frameNumber = 2

        buf[3].pinCount = 1
        buf[3].referenced = 1
        buf[3].frameNumber = 3

        buf[4].pinCount = 0
        buf[4].referenced = 1
        buf[4].frameNumber = 4
        # Consider the above buffer.
        # The clock algorithm starts at frame 0 (buf[0]) and tries to find a frame with pinCount =0
        # Clock finds buf[1], flips buf[1].referenced to 0 and continue
        # Clock finds buf[4], flips buf[4].referenced to 0 and continue
        # Clock finds buf[1] again and choose it

        print("2) Call the clock algorithm")
        clk = clock()
        if clk.pickVictim(buf) != 1:
            print(".... Error: clock algorithm did not chose frame 1.\n")
            status = False
            return status
        else:
            print(".... clock algorithm chose frame 1 successfully.")

        if buf[1].referenced != 0 or buf[4].referenced != 0:
            print(".... Error: clock algorithm did not update referenced attribute correctly.\n")
            status = False
            return status
        else:
            print(".... Clock algorithm updated referenced attribute correctly.\n")

        print("Test 1 completed successfully....\n")
        return status

    def test2(self):
        print("======= TEST2 ======")
        print("Scenario: more pages than frames (number of pages = 2 * number of frames)\n")

        status = True
        print("1) Create a buffer pool of five frames...\n")
        buf = bufferManager(5)

        print("2) Try to pin 10 new pages and write something in each page ")
        print("Requires that first five pages are evicted from buffer pool (and written to disk),")
        print("so the last five pages are pinned")
        print("")

        for i in range(10):
            pageNumber = i + 100
            pageX = buf.pin(pageNumber, True)
            pageX.content = "content {}".format(pageNumber)
            buf.unpin((pageNumber), True)

        print(".... Pinning of 10 pages suceeded\n")
        # buf.printBufferContent()

        print("3) Try to read the content of the 10 created pages")
        for i in range(10):
            pageNumber = i + 100
            pageX = buf.pin(pageNumber, False)
            if pageX.content != "content {}".format(pageNumber):
                print("....Error: page {} content is not correct\n".format(pageNumber))
                status = False
                return status
            buf.unpin((pageNumber), False)

        print(".... Reading the 10 pages succeeded.\n")
        print("Test2 completed successfully...\n")
        print("")
        return status

    def test3(self):
        status = True
        print("======= TEST3 ======")
        print("Scenario: Buffer pool full, cannot pin another page!\n")
        print("1) Create a buffer pool of five frames\n")
        buf = bufferManager(5)

        print("2) Pin five new pages without unpinning them\n")
        for i in range(5):
            pageNumber = i + 200
            pageX = buf.pin(pageNumber, True)

        print("3) Try to pin a sixth page, since buffer pool is full (all pages in buffer have pinCount =1),")
        print("we should get a BufferPoolFullError exception")

        pageNumber = 5 + 200
        try:
            pageX = buf.pin(pageNumber, True)
        except BufferPoolFullError:
            print(".... Expected BufferPoolFullError exception raised\n")
            status = True
        except:
            print(".... Unexpected error:\n", sys.exc_info()[0])
            status = False

        print("4) Now unpin one of the five pages, so we have one available frame\n")
        pageNumber = 4 + 200
        buf.unpin((pageNumber), False)

        print("5) Try to pin a sixth page, we should be able to do that this time")
        pageNumber = 5 + 200
        try:
            pageX = buf.pin(pageNumber, True)
            print(".... pinning a sixth page succeeded as expected\n")
        except:
            print(".... Unexpected error:\n", sys.exc_info()[0])
            status = False

        print("Test3 completed successfully...\n")
        print("")
        return status

    def test4(self):

        status = True
        print("======= TEST4 ======")
        print("Two transactions pin the same page with one of them writing to it\n")

        print("1) Create a buffer pool of five frames...\n")
        buf = bufferManager(5)

        pageNumber = 350
        print("2) Pin new page {}, modify its content, then unpin with dirtyBit=True\n".format(pageNumber))
        pageX = buf.pin(pageNumber, True)
        pageX.content = "content {}".format(pageNumber)
        buf.unpin((pageNumber), True)
        # buf.printBufferContent()

        pageNumber = 350
        print("3) Pin page {} again, then unpin with dirtyBit=False (e.g., a read-only transaction)".format(pageNumber))
        print("expecting that dirty bit stays True\n")
        pageX = buf.pin(pageNumber, False)
        buf.unpin((pageNumber), False)
        # buf.printBufferContent()

        print("4) Pin 5 pages so page {} is evicted from buffer pool".format(pageNumber))
        print("Dirty bit of Page {} should be True, thereofre, the page should be written to disk\n".format(pageNumber))

        for i in range(5):
            pageNo = i + 300
            pageX = buf.pin(pageNo, True)

        for i in range(5):
            pageNo = i + 300
            buf.unpin((pageNo), False)

        # buf.printBufferContent()

        pageNumber = 350
        print("5) pin page {} again and check its content (it should be read from disk)".format(pageNumber))
        pageX = buf.pin(pageNumber, False)
        # buf.printBufferContent()

        if pageX.content != "content {}".format(pageNumber):
            print("..... Error: page {} content is not correct\n".format(pageNumber))
            status = False
            return status
        else:
            print("..... Page {} content is correct!\n".format(pageNumber))

        print("Test4 completed successfully...\n")
        return status

    def test5(self):
        print("======= TEST5 ======")
        print("Scenario: more pages than frames (number of pages = (2 * number of frames) + 1)\n")

        status = True
        print("1) Create a buffer pool of five frames...\n")
        buf = bufferManager(5)

        print("2) Try to pin 11 new pages and write something in each page ")
        print(
            "Requires pinning the first five pages (600 to 604), then pinning the second five pages (605 to 609), then pinning the eleventh page (page #610)")
        print("")

        for i in range(11):
            pageNumber = i + 600
            pageX = buf.pin(pageNumber, True)
            pageX.content = "content {}".format(pageNumber)
            buf.unpin((pageNumber), True)

        print(".... Pinning of 11 pages suceeded\n")
        # buf.printBufferContent()

        print("3) Try to read the content of pages with odd page number")
        for i in range(1, 11, 2):
            pageNumber = i + 600
            pageX = buf.pin(pageNumber, False)
            if pageX.content != "content {}".format(pageNumber):
                print("....Error: page {} content is not correct\n".format(pageNumber))
                status = False
                return status
            print(pageX.content)
            buf.unpin((pageNumber), False)

        print(".... Reading pages with odd page number succeeded.\n")
        print("")

        print("4) Try to read the content of pages with even page number")
        for i in range(0, 11, 2):
            pageNumber = i + 600
            pageX = buf.pin(pageNumber, False)
            if pageX.content != "content {}".format(pageNumber):
                print("....Error: page {} content is not correct\n".format(pageNumber))
                status = False
                return status
            print(pageX.content)
            buf.unpin((pageNumber), False)

        print(".... Reading pages with even page number succeeded.\n")
        print("")

        print("Test5 completed successfully...\n")
        print("")
        return status


# ===============================================================
# Main Function

t = testingBM()
diskMnger = diskManager()

t1 = t.test1()

diskMnger.deleteAllPagesOnDisk()
t2 = t.test2()

diskMnger.deleteAllPagesOnDisk()
t3 = t.test3()

diskMnger.deleteAllPagesOnDisk()
# t4 = t.test4()

diskMnger.deleteAllPagesOnDisk()
t5 = t.test5()

if t1 and t2 and t3 and t4 and t5:
    print("All tests Completed sucessfully...")
else:
    print("Some tests have failed...")
