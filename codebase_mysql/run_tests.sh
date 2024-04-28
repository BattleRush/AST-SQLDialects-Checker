#!/bin/bash
cd codebase/mysql-test

# Tests to run
export TESTS="alias analyze"


# ./mysql-test-run.pl --extern socket=/home/ubuntu/Ongoing/AST/AST-SQLDialects-Checker/dbdata/mysql/mysqld/mysqld.sock \
#                     --client-bindir /home/ubuntu/Ongoing/AST/AST-SQLDialects-Checker/codebase_mysql/codebase/MYSQL_BUILD/runtime_output_directory \
#                      $TESTS
./mysql-test-run.pl --extern socket=/home/ubuntu/Ongoing/AST/AST-SQLDialects-Checker/dbdata/mysql/mysqld/mysqld.sock \
                     $TESTS

