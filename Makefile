gen-py:
	thrift -r -o lib --gen py lib/tpc.thrift
