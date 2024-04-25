all: mysql
clean:
	rm -rf codebase_mysql/codebase

mysql: codebase_mysql/codebase/MYSQL_BUILD/runtime_output_directory/
codebase_mysql/codebase/MYSQL_BUILD/runtime_output_directory/: codebase_mysql/codebase/MYSQL_BUILD/Makefile
	cd codebase_mysql/codebase/MYSQL_BUILD && make -j 8
codebase_mysql/codebase/MYSQL_BUILD/Makefile: codebase_mysql/codebase/
	mkdir -p codebase_mysql/codebase/MYSQL_BUILD; cd codebase_mysql/codebase/MYSQL_BUILD && cmake .. -DWITH_DEBUG=1 -DDOWNLOAD_BOOST=1 -DWITH_BOOST=~/boost_1_69_0
codebase_mysql/codebase/:
	cd codebase_mysql && git clone --depth 1 git@github.com:mysql/mysql-server.git codebase
