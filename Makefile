all: tps_over_time.png a_vs_b.png

tps_over_time.png: sysbench_output.txt
	./plot-sysbench-output-tps.py

a_vs_b.png: sysbench_output_doublewrite.txt  sysbench_output_nodoublewrite.txt
	./compare-sysbench.py

clean:
	rm -f tps_over_time.png a_vs_b.png
