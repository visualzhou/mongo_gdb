import re
import sys

SEP = "<SEP>"
SUB = "0x----------------"

class ThreadBackTrace:
  def __init__(self, name):
    self.name = name
    self.lines = []
     
  def merge_lines(self):
    self.one_line = SEP.join(self.lines)

  def split_lines(self):
    self.clean_lines = self.pattern.split(SEP)

  def replace_ox(self):
    pattern = self.one_line
    pattern = re.sub(r'0x\w{4,}', SUB, pattern)
    pattern = re.sub(r'=\d+', "=<NUMBER>", pattern)
    self.pattern = pattern

def get_uniq_threads(threads):
  h = {}
  for t in threads:
    if not t.pattern in h:
      h[t.pattern] = []
    h[t.pattern].append(t)

  return h.values()      

def parse(filename):
  cur_thread = ThreadBackTrace("<noname>")
  all_threads = []
  with open(filename, 'r') as gdb_output:
     for line in gdb_output:
       if line.startswith("Thread"):
         if cur_thread.lines:
           all_threads.append(cur_thread)
         cur_thread = ThreadBackTrace(line) 
       elif line.strip():
           cur_thread.lines.append(line)
  if cur_thread.lines:
    all_threads.append(cur_thread)
  print "All threads: ", len(all_threads)

  for t in all_threads:
    t.merge_lines()
    t.replace_ox()
    t.split_lines()

  uniq_threads = get_uniq_threads(all_threads)
  print "Unique threads:", len(uniq_threads)
  for t in uniq_threads:
    print len(t), "times", t[0].name,
    for l in t[0].lines:
      print l,
    print
  
def main():
  if len(sys.argv) != 2:
      print "Usage: python {} <bt_output_file>".format(sys.argv[0])
      return

  parse(sys.argv[1])


if __name__ == "__main__":
  main()
