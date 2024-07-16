Table of Contents
=================

# Plot sysbench tps output with matplotlib and pandas

This let's you collect sysbench output and then graph it. If you have two
different runs you can collect both output and compare them on the same graph
too. The container mysql:8.0 is used for simplicity.

# Usage

```bash
./0004-run-sysbench.sh | tee -a sysbench_output.txt
```

# Initial setup

Although this tree is just about graphing the TPS, it can be used to also
ramp up a MySQL container and a few others to initialize sysbench tables,
populate them, start sysbench and collect telemetry. That is just optional
scripts you can use for further analysis and is beyond the scope of this
tree, the scripts are just provided for convenience. Proper integration for
automation in full scope will be done later in kdevops.

# Example output of a single run zoomed out

We start plot at 0 on the y axis.

<img src="tps_over_time_zoomed_out.png" align=center alt="tps over time">

# Example output of a single run zoomed in

We start plot at the first TPS value on the y axis.

<img src="tps_over_time_zoomed_in.png" align=center alt="tps over time">

# Example output of comparing two runs zoomed out

We start plot at 0 on the y axis.

<img src="a_vs_b_zoomed_out.png" align=center alt="a Vs b TPS">

# Example output of comparing two runs zoomed in

We start plot at the first TPS value on the y axis.

<img src="a_vs_b_zoomed_in.png" align=center alt="a Vs b TPS">

# Preconditioning

There are two parts to pre-conditioning:

  * pre-fill the drive
  * steady state detection

You may just want to change the minutes for hours.  Note that if you use
runtime=6h and ss_dur=4h it means that we can bail early if steady state is
attained before 6 hours. The 6 hours would be the upper bound.

Use:

```bash
# We pre-fill twice
./ss/pre-fill.sh /dev/nvme0n1
./ss/pre-fill.sh /dev/nvme0n1

# First steady state for IOPS
fio --warnings-fatal --output=ss_iops.json --output-format=json+ ss/0001-fio_ss_generic-random-iops.ini

# Second seteady state, now for throughput
fio --warnings-fatal --output=ss_iops.json --output-format=json+ ss/0002-fio_ss_generic-random-bw.ini

# XXX: fio needs latency steady-state
```

## Parsing json output from fio steady state

Let's process the sample file we used which just had a runtime=6m and ss_dur=4m.

```bash
# Install jq
apt-get install jq

# Let's get the steady state job descriptions we defined ourselves

# First the iops steady state results file
jq '.jobs[0].jobname,.jobs[0].steadystate.ss,.jobs[1].jobname,.jobs[1].steadystate.ss' ss/ss_iops.json 
"steady-state-mean-iops"
"iops:20.000000%"
"steady-state-slope-iops"
"iops_slope:10.000000%"

# Second the throughput steady state results file
jq '.jobs[0].jobname,.jobs[0].steadystate.ss,.jobs[1].jobname,.jobs[1].steadystate.ss' ss/ss_bw.json 
"steady-state-mean-bw"
"bw:20.000000%"
"steady-state-slope-bw"
"bw_slope:10.000000%"

# Now see if we attained steady state given the formulation and requirements
# we had specified for IOPS.
jq '.jobs[1].steadystate.attained,.jobs[1].steadystate.attained' ss/ss_iops.json
1
1

# How about for throughput
jq '.jobs[1].steadystate.attained,.jobs[1].steadystate.attained' ss/ss_bw.json
1
1

# Count how many entries we collected for IOPS
jq '.jobs[0].steadystate.data.iops,.jobs[0].steadystate.data.bw,.jobs[1].steadystate.data.iops,.jobs[1].steadystate.data.bw | length' ss/ss_iops.json
240
240
240
240

# OK how aobut for throughput
jq '.jobs[0].steadystate.data.iops,.jobs[0].steadystate.data.bw,.jobs[1].steadystate.data.iops,.jobs[1].steadystate.data.bw | length' ss/ss_bw.json
240
240
240
240
```

## Plotting steady state

There's a work in progress plot attempt of the steady state output files there.

License
-------

This work is licensed under the copyleft-next-0.3.1, refer to the [LICENSE](./LICENSE) file
for details. Please stick to SPDX annotations for file license annotations.
If a file has no SPDX annotation the copyleft-next-0.3.1 applies. We keep SPDX annotations
with permissive licenses to ensure upstream projects we embraced under
permissive licenses can benefit from our changes to their respective files.
Likewise GPLv2 files are allowed as copyleft-next-0.3.1 is GPLv2 compatible.
