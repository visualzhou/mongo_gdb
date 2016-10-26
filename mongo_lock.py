import gdb
import gdb.printing

import re
import struct

def find_func_block(block):
  if not block:
    return None

  if block.function:
    return block

  return find_func_block(block.superblock)

def find_frame(function_name_pattern, frame = None, times = 10):
  if (times == 0):
    return None

  if not frame:
    frame = gdb.selected_frame()
  
  try:
    block = find_func_block(frame.block())
    if block:
      if re.search(function_name_pattern, block.function.name):
        print("found", function_name_pattern, block.function)
        return frame
  except RuntimeError as err:
    # print("ignoring ", err)
    pass

  if frame.older():
    return find_frame(function_name_pattern, frame.older(), times - 1)


def get_mutex_holder(sym, frame):
  value = sym.value(frame)
  holder = value["_M_mutex"]["__data"]["__owner"]
  return holder, value.address

def find_mutex_holder():
  frame = find_frame(r'std::mutex::lock\(\)')
  if not frame:
    return
 
  # Waiting for mutex locking!
  mutex_this, _ = gdb.lookup_symbol("this", frame.block())
  mutex_value = mutex_this.value(frame)
  mutex_holder = mutex_value["_M_mutex"]["__data"]["__owner"]

  # Process ID/PID,  Lightweight Process ID (LWPID), Thread ID (TID)
  me = gdb.selected_thread()
  tid = me.ptid[1] if me.ptid[1] > 0 else me.ptid[2]
  # print("Mutex:", tid, "is waiting on mutex at", mutex_value.address, "held by", mutex_holder)
  print("Mutex at", mutex_value.address, "held by thread tid", mutex_holder)
  return

  
def find_lock_manager_holders():
  # frame = find_frame(r'lockComplete')
  frame = find_frame(r'mongo::LockerImpl\<.*\>::')
  if not frame:
    return

  old_frame = gdb.selected_frame()
  frame.select()

  locker_ptr_type = gdb.lookup_type("mongo::LockerImpl<false>").pointer()
  # grantedList = gdb.parse_and_eval("mongo::getGlobalLockManager()->_getBucket(resId)->findOrInsert(resId).grantedList")
  lock_head = gdb.parse_and_eval("mongo::getGlobalLockManager()->_getBucket(resId)->findOrInsert(resId)")
  grantedList = lock_head.dereference()["grantedList"]
  lock_request_ptr = grantedList["_front"]
  while lock_request_ptr != 0:
    lock_request = lock_request_ptr.dereference()
    locker_ptr = lock_request["locker"]
    locker_ptr = locker_ptr.cast(locker_ptr_type)
    locker = locker_ptr.dereference()
    thread_id = locker["_threadId"]["_M_thread"]
    print("MongoDB Lock at", lock_head, "held by thread id 0x{:x}".format(int("{}".format(thread_id))), lock_request["mode"])

    lock_request_ptr = lock_request["next"]

  # resume old frame
  old_frame.select()

def show_lock_holders():
  find_mutex_holder()
  find_lock_manager_holders()

