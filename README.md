A set of gdb pretty printers for objects in the MongoDB source code.

### Install
If you find the need to bypass the printers and look at the raw fields, use
the /r flag to print.

To use add the following lines to your .gdbinit, adjusting the path as needed:

```python
python
import sys
import os
try:
    sys.path.insert(0, os.path.expanduser('~/10gen/mongo_gdb/'))
    import mongo_printer
    mongo_printer.register_mongo_printers()
    # Show mutex and MongoDB lock holders
    import mongo_lock
except Exception:
    print('Error loading mongo_printer and mongo_lock')
    pass
end

### Run mongo_lock.show_lock_holders()
```

### Print out lock holders

```
(gdb) thread apply all python mongo_lock.show_lock_holders()

Thread 4 (Thread 0x7ffff49ea700 (LWP 13813)):
found std::mutex::lock\(\) std::mutex::lock()
Mutex at 0x7ffff49e97c8 held by thread tid 13811

Thread 3 (Thread 0x7ffff51eb700 (LWP 13812)):
found std::mutex::lock\(\) std::mutex::lock()
Mutex at 0x7ffff51ea7c8 held by thread tid 13811

Thread 2 (Thread 0x7ffff59ec700 (LWP 13811)):
found mongo::LockerImpl\<.*\>:: mongo::LockerImpl<false>::lockComplete(mongo::ResourceId, mongo::LockMode, unsigned int, bool)
MongoDB Lock at 0x7ffff65cfb80 held by thread id 0x7ffff49ea700 mongo::MODE_IX
MongoDB Lock at 0x7ffff65cfb80 held by thread id 0x7ffff51eb700 mongo::MODE_IX

Thread 1 (Thread 0x7ffff7fd9cc0 (LWP 13807)):
(gdb)
```

### Dedup threads in gdb backtrace output
The script expects each thread `bt` output starts with `Thread XXXX`.
You may find [logging gdb output](https://sourceware.org/gdb/onlinedocs/gdb/Logging-Output.html) useful.

```sh
python parse_gdb_output.py <bt_output_file>
```
