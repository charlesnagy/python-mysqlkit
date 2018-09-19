.. _gtid:


GTID related objects
====================

MySQL executed_gtid_set:

.. code:: mysql

    Executed_Gtid_Set: 2f4a5622-45dc-11e5-9512-069f92734481:1-42:45-50
                       \-------------- UUID --------------/
                                                   GTIDRange --> \---/

                                          GTIDRangeList --> \--------/

                       \-------------- GTIDSet ----------------------/


GTIDRange
---------

The class can be instantiated with string literal or `first` and `last` parameter.

.. important::

  The range in **inclusive on both end** to be consistent with MySQL terminology

.. code:: python

    In [1]: from mysqlkit.rpl import gtid

    In [2]: r1 = gtid.GTIDRange(1, 29)

    In [3]: r2 = gtid.GTIDRange('1-29')

    In [4]: r1 == r2
    Out[4]: True


Defined operations:

* Addition
* Substraction
* Containment
* Comparisons

Defined methods:

* is_overlapping
* is_consecutive

**Examples**

.. code:: python

    In [1]: from mysqlkit.rpl import gtid

    In [2]: r1 = gtid.GTIDRange(1, 29)

    In [3]: r2 = gtid.GTIDRange(30, 41)

    In [4]: r3 = gtid.GTIDRange(15, 32)

    In [5]: r4 = gtid.GTIDRange(91, 105)

    In [6]: r1.is_consecutive(r2)
    Out[6]: True

    In [7]: r2.is_consecutive(r1)
    Out[7]: False

    In [8]: r1.is_overlapping(r2)
    Out[8]: False

    In [9]: r1.is_overlapping(r3)
    Out[9]: True

    In [10]: r1.is_overlapping(r4)
    Out[10]: False

    In [11]: r1 < r2 < r4
    Out[11]: True

    In [12]: r1 < r3
    Out[12]: True

    In [13]: r2 < r3
    Out[13]: False

    In [14]: r1 + r2 + r4
    Out[14]: <GTIDRangeList:[1-41:91-105]>

    In [15]: r1 - r3
    Out[15]: <GTIDRangeList:[1-14]>

    In [16]: r3 in (r1 + r2)
    Out[16]: True


GTIDRangeList
-------------

-- This class represents a list of ranges for **any** source uuid.

Similar to GTIDRange, GTIDRangeList can be instantiated with string lateral (from MySQL) or list of GTIDRanges or tuples.

.. code:: python

    In [1]: from mysqlkit.rpl import gtid

    In [2]: gtid.GTIDRangeList('140')
    Out[2]: <GTIDRangeList:[140]>

    In [3]: gtid.GTIDRangeList('1-141', '145-197')
    Out[3]: <GTIDRangeList:[1-141:145-197]>

    In [4]: gtid.GTIDRangeList('1:8-99:102-139:145-197')
    Out[4]: <GTIDRangeList:[1:8-99:102-139:145-197]>

    In [5]: gtid.GTIDRangeList(gtid.GTIDRange(1, 7), gtid.GTIDRange(9))
    Out[5]: <GTIDRangeList:[1-7:9]>


Defined operations:

* Addition
* Substraction
* Equality
* Containment

Defined methods:

* count - return the number of transactions in a range list


GTIDSet
-------

This is the main class that prepresents the `executed_gtid_set` or `retrieved_gtid_set` from MySQL directly and
    can be used for comparing these values accross servers.

.. code:: python

    In [1]: from mysqlkit.rpl import gtid


    In [2]: master_executed = gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-27')

    In [3]: slave_executed = gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23:27')

    In [4]: master_executed - slave_executed
    Out[4]: <GTIDSet:3E11FA47-71CA-11E1-9E33-C80AA9429562:24-26>

    In [5]: trx_behind_master = (master_executed - slave_executed).count()

    In [6]: print trx_behind_master
    3

    In [7]: master_executed.count()
    Out[7]: 27