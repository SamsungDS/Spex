from typing import TypeVar, Protocol, Union, Optional, Generic, cast


_T_co = TypeVar("_T_co", covariant=True)
T = TypeVar("T")


class SupportsNext(Protocol[_T_co]):
    def __next__(self) -> _T_co:
        ...


class Stream(Generic[_T_co]):

    def __init__(self, iterable: SupportsNext[_T_co]):
        self.__iter = iterable
        self.__end_of_iter = object()
        self.__current: Union[_T_co, object] = next(iterable, self.__end_of_iter)

    def end(self) -> bool:
        return self.__current is self.__end_of_iter

    def peek(self) -> _T_co:
        if self.__current == self.__end_of_iter:
            raise StopIteration("no element, use Stream.end to test for elements")
        return cast(_T_co, self.__current)

    def consume(self) -> _T_co:
        val = self.__current
        if val == self.__end_of_iter:
            raise StopIteration("no element, use Stream.end() to test for elements")
        self.__current = next(self.__iter, self.__end_of_iter)
        return cast(_T_co, val)
