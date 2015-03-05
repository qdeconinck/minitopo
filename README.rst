What ?
======

Simple tool, based on `mininet <http://mininet.org/>`_, to boot a simple network
with n paths and run experiments between two hosts.


Usage
=====

.. code-block:: console

        ./mpPerf -t topo -x xp

The format for the topo file and xp file is simple but could be different based
on the type of topo or experiments. Details should follow.

basic Example
=============

1. Get the CLI
--------------

.. code-block:: console

        ./mpPerf -t conf/topo/simple_para

The content of simple_para is:

.. code-block:: console

        desc:Simple configuration with two para link
        topoType:MultiIf
        leftSubnet:10.0.
        rightSubnet:10.1.
        #path_x:delay,queueSize(may be calc),bw
        path_0:10,10,5
        path_1:40,40,5
        path_2:30,30,2
        path_3:20,20,1

``topoType`` just specifies that we want to have multiple interfaces, one for
each path.

Each path is defined by 3 values, delay (one way, int, in ms), queue_size (int, 
in packets), and bandwidth (float, in mbit/s).

Once the configuration is up, you have access to the CLI. You can check route
configuration (policy routing etc.) Just by issuing regular commands preceded
by ``Client`` or ``Server``

2. Simple experiment
--------------------

.. code-block:: console

        ./mpPerf -t conf/topo/simple_para -x conf/xp/4_nc

This command will start the same topology and run the experiment defined by 4_nc
The result for this experiment is a simple pcap file.

They are other options and experiments, but the documentation is still to be
written.
