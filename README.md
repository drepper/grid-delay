Demonstration of Delays in 2-D Computing Grid
=============================================

This is a simulation of the progress made in a 2-D computation grid.
In such a grid the computations are done in (time) steps.  Before the
next step can be started all neighboring nodes (eight in this case,
except on the edges) must have finished the previous round.  This is
in many computations necessary to exchange information about the
results of the finished step so that non-local data can be taken into
account during the computation of the next step.

One example would be the computation of trajectories of objects with
mass.  In theory every object has an effect on any other object but
this would slow down the computation tremendously.  Instead, as an
approximation only the objects in the vacinity are taken into account.

If each node performs the computation for some part of space (2D, 3D,
or whatever) then only masses in the neighboring nodes need to be know.
This can be mapped nicely to a grid as in this example.

Animate
-------

The python program creates SVG files as output.  These can be looked at
with `eog` or similar tools in sequence.  Or: one can create an animated
GIF:

    convert -delay 40 -loop 1 gen-t????.svg gird-movie.gif
