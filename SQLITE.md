# SQLite shenanigans
Replace the `do_execsql_test` function body inside `tester.tcl` in the SQLite submodule with the following snippet:


```tcl
proc do_execsql_test {args} {
  puts "hello tester"
  # print args
  puts $args
  set db db
  if {[lindex $args 0]=="-db"} {
    set db [lindex $args 1]
    set args [lrange $args 2 end]
  }

  if {[llength $args]==2} {
    foreach {testname sql} $args {}
    set result ""
  } elseif {[llength $args]==3} {
    foreach {testname sql result} $args {}

    # With some versions of Tcl on windows, if $result is all whitespace but
    # contains some CR/LF characters, the [list {*}$result] below returns a
    # copy of $result instead of a zero length string. Not clear exactly why
    # this is. The following is a workaround.
    if {[llength $result]==0} { set result "" }
  } else {
    error [string trim {
      wrong # args: should be "do_execsql_test ?-db DB? testname sql ?result?"
    }]
  }

  fix_testname testname
  puts "----START $testname"
  puts ">>>>\n $sql \n<<<<"
  puts ";;;;\n $result \n::::"
  puts "----END"
  #puts "Running SQL: $sql"
  #puts "Expecting: $result"
  #puts "###################"
  uplevel do_test                 \
      [list $testname]            \
      [list "execsql {$sql} $db"] \
      [list [list {*}$result]]

  puts "--------------"
}
```

To run the SQLite test suite run the following commands: 
```bash
./configure
make
make testfixture
tclsh ./test/testrunner.tcl all
```

After the test suite has finished, there should be a testrunner.log. This file will be used by the parser to extract the SQL queries.
