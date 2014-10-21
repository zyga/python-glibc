CFLAGS += -Wall -Werror -std=c99
.PHONY: all clean
all: demo3
demo3: demo3.o
clean:
	rm -f *.o demo3

.PHONY: test-glibc-vs-python
diff-glibc-vs-python:  # Compare Strace of python3 epoll with glibc epoll
	PYTHONPATH=.. strace -e abbrev=none -e trace=epoll_wait,epoll_create,epoll_create1,epoll_ctl -o python-glibc.strace python3 ./demo3.py ls > /dev/null
	PYTHONPATH=.. strace -e abbrev=none -e trace=epoll_wait,epoll_create,epoll_create1,epoll_ctl -o python-epoll.strace python3 ./demo3-python-epoll.py ls > /dev/null
	diff -u python-glibc.strace python-epoll.strace || :
