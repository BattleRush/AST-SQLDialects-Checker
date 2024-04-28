all: mysql
clean:
	rm -rf codebase_mysql/codebase

mysql: mcodebase_mysql/codebase/runtime_output_directory/

# Build mysql
codebase_mysql/codebase/runtime_output_directory/: codebase_mysql/codebase/Makefile
	cd codebase_mysql/codebase && make -j 16
codebase_mysql/codebase/Makefile: codebase_mysql/codebase/
	mkdir -p codebase_mysql/codebase; cd codebase_mysql/codebase && cmake . -DWITH_DEBUG=1 -DDOWNLOAD_BOOST=1 -DWITH_BOOST=~/boost_1_69_0 -DFORCE_INSOURCE_BUILD=1
codebase_mysql/codebase/:
	mkdir -p codebase_mysql; cd codebase_mysql && git clone --depth 1 git@github.com:mysql/mysql-server.git codebase
