#!/usr/bin/env python

import argparse as ap
import os.path
from numjuggler import numbering as mn
from numjuggler import parser as mp
from numjuggler import ri_notation as rin


# help messages already wrapped:
help_c = """
Cell number increment. If an integer is given, it is added to all cell numbers
(negative entries are valid as well). If "i" is given, cell numbers are
replaced by their sequence numbers, in the order as they appear in the input
file (the 1-st cell becomes number 1, etc)
"""[1:]  # here I remove the 1-st newline

help_s = '{} number increment, similar to "-c"'

dhelp = {}
dhelp['mode'] = """
EXECUTION MODES
---------------

The "--mode" argument defines the execution mode of the script. It can have the
following string values:


renum:
    The default mode. Cells, surfaces, materials and universes are renamed
    according to the -c, -s, -m, -u or --map command line options. The original
    MCNP input file is not modified, the input file with renamed elements in
    written to std.out.


info:
    The input file is analysed and ranges of used numbers for cells, surfaces,
    ets. is written to std.out. Note that output of this mode can be used
    (after necessary modifications) as input to the --map option.

    The first two columns specify type (cells, surfaces, etc.) and the range of
    used numbers. The third column shows the amount of numbers in current range,
    and the last column shows how many numbers left unused between the current
    and previous ranges.


wrap:
    Wrap lines in the MCNP input file to fit the 80-chars limit. Wrapped only
    meaningful parts of the lines: if a line exceed 80 characters due to
    comments (i.e.  any entries after "$" or "&"), it is not wrapped.


rems:
    Replace multiple spaces with only one space. This operation is performed
    only to the meaningful parts of the input file, i.e. comments are leaved
    unchanged.


remc:
    remove all external comment lines (external means between cards).


uexp:
    Add explicit "u=0" to cells with no "u" parameter. This can be useful when
    combining several input files into one model using universes. When cells
    have explicit zero universes, they can be renumbered using the -u or --map
    option in subsequent runs.  

    Another universe can be specified with the -u option. IN this case, the whole option should 
    be specified, i.e. -u ' u=1 '

    The -c option can be used to specify cells to be handled. Examples:

         -c "1 --150" -- add universe option only to these cells.
         -c "!2" -- do not add universe to cell 2, even if it safisfies above criteria

split: 
    Split input into several files containing separate blocks. Output is written
    to files

        inp.1message
        inp.2title
        inp.3cells
        inp.4surfaces
        inp.5data

    where inp is replaced by the name of the ofiginal input file. Note that
    separate blocks do not contain blank lines. In order to concatenate block files 
    together into a single input, one needs to insert blank lines:

    > numjuggler --mode split inp_
    > cat inp_.[1-5]* > inp2_          # inp2_ lacks all blank lines
    > echo '' > bl
    > cat inp_.1* bl inp_.2* bl inp_.3* bl inp_.4* bl inp_.5* bl > inp3_ # inp3_ is equivalent to inp_


mdupl:
    remove duplicate material cards. If an input file contains several mateiral
    cards with the same name (number), only the first one is kept, the other
    are skipped. 


matan:
    Compare all meterials and list possible duplicates. 

sdupl:
    Report duplicate (close) surfaces.


msimp:
    Simplify material cards.
    
    
extr:
    Extract the cell specified in the -c keyword together with materials, surfaces 
    and transformations.

    If the first entry of the -c keyword is `!`, extract all but the cells specified after.

    
    
nogq:
    Replaces GQ cards representing a cylinder with c/x plus tr card. In some
    cases this improves precision of cylinder's representations and helps to
    fix lost particle errors.

    Transformation card numbering starts from the number specified in -t argument.

    If -c is given and differs from "0", the original GQ cards remain in the
    input, but commented out.  Otherwise (i.e. by default), they disappear from
    the input.
    
    
count:
    Returns a list of cells with the number of surfaces used to define cell's
    geometry.  Two values returned for each cell: total amount of surfaces
    mentioned in the cell geometry, and the number of unique surfaces (that is
    equal or less than the former). 
    
    Cells with total number of surfaces exceeding 100 (or the value given as 
    `-s` command line parameter) are denoted in the output with `*`
    
    
nofill:
    Under counstruction: Removes all 'fill=' keywords from cell cards.

fillempty:
    Add to all void non-filled cells with importance > 0 ``FILL = N``, where N
    is specified in the ``-u`` argument. When a material name is given with the
    -m argument, cells filled with this material are filled with N, instead of
    void cells.

    When a file is given with the --map option, a list of cells is read from this file,
    and the "fill=" is added to these cells only, independent on cell's importance or material.
    
    UPD: the content of -u option is copied into the input file as is. For example, to specify
    transformation in-place: -u '*fill=1 (0 0 5)'.

    
matinfo:
    Output information about how materials are used: for each material list of cells with density and universe.
    
    
uinfo:
    For each universe defined in the input file, return a list of cells in this universe.


impinfo:
    List all cells with zero importances.
    
    
sinfo:
    For each surface defined in the input file, return the list of cells where it is used.

    At the end list all used types of surfaces.
    
vsource:
    Output data cards describing source for computation of volumes. Model
    dimensions must be specified in the -c option as a rcc that circumscribes
    the model. For example, 

    --mode vsource -c "10 20 -10 10 -20 20"

    will generate planar sources for the box 10 < x < 20, -10 < y < 10, -20 < z < 20.

    --mode vsource -s 100 

    will generate spherical source for the sphere 100.

    --mode vsource -s "10 11 12 13 14 15"

    will generate planar source based on parameters of planes 10 -- 15 (these
    surfaces must be px, py and pz planes).


tallies:    
    Output tally cards for calculation of volumes in all cells. Tally number
    can be given with the -s option, and with non-zero -u one can specify cells
    of particular universe.


addgeom:
    appends strings, specified in --map file  to geometry definition of cells.
    Example of the map file:

    10  -1 , #12 #35
    11   1 , #12 #35
    135

    First entry -- cell, which geometry should be modified. Second entry till
    comma ('-1' and '1' in the above example) will be prepended to the cell's
    existing geometry definition, the rest after the comma will be appended
    after the existing geometry definition.

    If the cell number is not followed by any entry (including the comma), this cell
    will be removed from the resulting input file. In the above example, cell 135 will
    be removed.


merge:
    put two input files into a single file. Second input file is given in the -m option. 


remu:
    Remove all cells that belong to the universe specified in the -u option. SUrfaces that
    are used only for these cells are removed also.


zrotate:
    rotate gometry around z-axis to the angle specified in -c parameter.
    Rotation is applied by defining the transformation card and applying it to
    surfaces without transformations. And all existing pure rotational
    transformations are changed.

annotate:
    Adds text from map file as multiline comment right after the title.


getc:
    Extract comments taking more than 10 (or given by -c option) lines.


"""


dhelp['map'] = """
MAP FILE GENERAL INFO
---------------------

Mapping rules can be specified in a separate file that is read when --map
option is given.

Different from the -c, -s, -m and -u options, in the map file one can specify
mapping rules for separate ranges. Ultimately, all new cell, surface, material
or universe names can be given explicitly.


MAP FILE FORMAT
---------------

The map file consists of lines of the following form:

    t [range]: [+-]D

The first entry, t, is a one character type specification: "c" for cells, "s"
for surfaces, "m" for materials and "u" for universes.

It is optionally followed by the range specifier that can be one number, for
example "10", or two numbers delimited by two dashes, for example "10 -- 25". If
the range is omitted, the line defines the default mapping, i.e. it is applied
to elements not entering to all other ranges.

The semicolon, ":", delimits the range specification from the specification of
the mapping rule.  It is followed by an integer, optionally signed. This
integer defines an increment to which numbers in the current range are
increased. The mapping is than N -> N+D, where N is the original number from the
range [N1, N2].

When unsigned integer "D" is given on the line with range specification, i.e.
with "N1" or "N1 -- N2", it is considered as the first element of the mapped
range. Mapping in this case is N -> N+D-N1, where N in [N1, N2].


MAP FILE EXAMPLES
-----------------

In the example below, cells from 1 to 10 inclusive are renamed to the range from
11 to 20, cell 200 is renamed to 250 and to all other cells numbers are
incremented by 1000:

    c 1 -- 10: +10    # explicit sign means increment
    c 200:     250    # no sign means new number
    c:        1000    # all other cell numbers increment by 1000

Another example specifies that only universe number 0 should be modified:

    u 0: 10          # universe 0 will become number 10
    u: 0             # not necessary, while the trivial mapping is by default.


Provide all cell numbers explicitly (assume that input file has cells from 1 to
5):

    c 1: 12
    c 2: 14
    c 3: 16
    c 4: 18
    c 5: 20

Note that the --mode info option gives a list of all used ranges and can be used
as a basis for the mapping file.

Only lines beginning with "c", "s", "u" or "m" and having the semicolon ":" are
taken into account; all other lines are ignored. After the semicolon, only one
entry is taken into account.

"""

dhelp['examples'] = """
INVOCATION EXAMPLES
-------------------

Get extended help:

  > mcnp.juggler -h mode
  > mcnp.juggler -h map


Prepare model for insertion into another as universe 10:

  > mcnp.juggler --mode uexp inp > inp1     # add u=0 to real-world cells
  > echo "u0: 10 " > map.txt                # generate mapping file
  > mcnp.juggler --map map.txt inp1 > inp2  # replace u=0 with u=10
  > mcnp.juggler --mode wrap inp2 > inp3    # ensure all lines shorter 80 chars.


Rename all cells and surfaces by adding 1000:

  > mcnp.juggler -s 1000 -c 1000 inp > inp1
  > mcnp.juggler --mode wrap inp1 > inp2    # ensure all lines shorter 80 chars.


Rename all cells and surfaces by incrementing numbers as they appear in the
input file. To check renumbering, store log and use it on the next step as the
map file to perform the reverse renumbering.  Finally, remove extra spaces from
the resulting file and original one, in order to simplify visual comparison:

  > mcnp.juggler -c i -s i --log i1.log i1 > i2
  > mcnp.juggler --map i1.log i2 > i3       # apply log as map file for reverse renubmering
  > mcnp.juggler --mode rems i1 > c1        # remove extra spaces from original input
  > mcnp.juggler --mode rems i3 > c3        # and from result of reverse renumbering
  > vimdiff c1 c3                           # compare files visually


"""

dhelp['limitations'] = """
LIMITATIONS
-----------

Cell parameters can be read only from the cell cards block. Cell parameters
specified in the data cards block are ignored.

Only subset of data cards is parsed to find cell, surface, etc. numbers. For
example, cell and surface numbers will be recognized in a tally card, but
material numbers will not be found in tally multiplier card. Also, cell and
surface numbers in the source-related cards are nor recognized.

Only a subset of execution modes were tested on the C-lite model. Current
implementation is rather ineffective: complete renumbering of cells and
surfaces in C-lite takes 5 -- 10 min.


"""

descr = """
Renumber cells, surfaces, materials and universes in MCNP input file. The
original MCNP input file name must be given as command line option, the modified
MCNP input file is written to std.out." """[1:]

# dhelp keys as a string, with the last ',' replaced with 'or' for more humanity
dhelp_keys = str(dhelp.keys())[1:-1][::-1].replace(',', ' ro ', 1)[::-1]

epilog = """
Specify {} after -h for additional help.
"""[1:].format(dhelp_keys)


def main():
    p = ap.ArgumentParser(prog='numjuggler', description=descr, epilog=epilog) # formatter_class=ap.RawTextHelpFormatter)
    p.add_argument('inp', help='MCNP input file')
    p.add_argument('-c', help=help_c, type=str, default='0')
    p.add_argument('-s', help=help_s.format('Surface'), type=str, default='0')
    p.add_argument('-m', help=help_s.format('Material'), type=str, default='0')
    p.add_argument('-u', help=help_s.format('Universe'), type=str, default='0')
    p.add_argument('-t', help=help_s.format('Transformation'), type=str, default='0')
    p.add_argument('--map', type=str, help='File, containing descrption of mapping. When specified, options "-c", "-s", "-m" and "-u" are ignored.', default='')
    p.add_argument('--mode', type=str, help='Execution mode, "renum" by default', choices=['renum', 'info', 'wrap', 'uexp', 'rems', 'remc', 'split', 'mdupl', 'matan', 'sdupl', 'msimp', 'extr', 'nogq', 'count', 'nofill', 'matinfo', 'uinfo', 'impinfo', 'fillempty', 'sinfo', 'vsource', 'tallies', 'addgeom', 'merge', 'remu', 'zrotate', 'annotate', 'getc'], default='renum')
    p.add_argument('--debug', help='Additional output for debugging', action='store_true')
    p.add_argument('--log', type=str, help='Log file.', default='')

    # parse help option in another parser:
    ph = ap.ArgumentParser(add_help=False)
    ph.add_argument('-h', help='Print help and exit', nargs='?', default='', const='gen')
    harg, clo = ph.parse_known_args()
    if harg.h:
        if harg.h == 'gen':
            p.print_help()
        elif harg.h in dhelp.keys():
            print dhelp[harg.h]
        else:
            print 'No help for ', harg.h
            print 'Available help options: ', dhelp_keys
    else:
        args = p.parse_args(clo)
        if args.debug:
            # args.inp can be a path with folders. Ensure that the prefix
            # 'debug.juggler' is added to the base filename only.
            d, f = os.path.split(args.inp)
            debug_file_name = os.path.join(d, 'debug.juggler.' + f)
            # print
            # print 'Debug info written to ', debug_file_name
            # print
            debuglog = open(debug_file_name, 'w')
            print >> debuglog, 'command line arguments:', args
        else:
            debuglog = None

        # process input file only once:
        cards = list(mp.get_cards(args.inp, debuglog))

        if args.mode == 'info':
            indent = ' '*8
            for c in cards:
                c.get_values()
            d = mn.get_numbers(cards)

            if args.debug:
                types = sorted(d.keys())
            else:
                types = ['cel', 'sur', 'mat', 'u', 'tal', 'tr']
            for t in types:
                if t[0] <> '#': # for meaning of '#' see parser.
                    nset = set(d.get(t, []))
                    print '-'* 40, t, len(nset)
                    print '-'* 20, t, ' list', ' '.join(map(str, rin.shorten(sorted(nset))))
                    rp = None
                    for r1, r2 in mn._get_ranges_from_set(nset):
                        print '{}{:>3s}'.format(indent, t[0]),
                        if r1 == r2:
                            rs = ' {}'.format(r1)
                        else:
                            rs = ' {} -- {}'.format(r1, r2)
                        if rp != None:
                            fr = '{}'.format(r1 - rp - 1)
                        else:
                            fr = ''
                        ur = '{}'.format(r2 - r1 + 1)
                        print '{:<30s} {:>8s} {:>8s}'.format(rs, ur, fr)
                        rp = r2
        elif args.mode == 'ext':
            # output list of cells for ext:n card
            for c in cards:
                c.get_values()
            d = mn.get_numbers(cards)
        # elif args.mode == 'tallies':
        #     # generate tally cards for volume in each cell
        #     n = int(args.s) # as tally number
        #     u = args.u # specify cells of particular universe only
        #     if args.m != '0':
        #         fmt = args.m
        #     else:
        #         fmt = '{}'
        #     cset = set()
        #     for c in cards:
        #         c.get_values()
        #         if c.ctype == mp.CID.cell:
        #             cu = c.get_u()
        #             if u == '_' or cu == int(u) or (cu == None and int(u) == 0):
        #                 cset.add(c.name)
        #         elif c.ctype ==  mp.CID.surface:
        #             break
        #     print 'f{}:n {}'.format(n, fmt.format(' '.join(map(str, rin.shorten(sorted(cset))))))
        #     print 'sd{} 1 {}r'.format(n, len(cset)-1)

        elif args.mode == 'tallies':
            # New version: tally number and universes should be specified in the format string passed via -m argument.
            # -m must be present and have form: 'f4:n (u4 < u5)', where uN -- placeholders for lists of cells
            # that belong to universe N.

            import re
            r = re.compile('(u)(\d+)')

            csets = {}
            ulst = []
            fmt = args.m[:]
            for s in r.findall(args.m):
                ss = s[0] + s[1]
                u = int(s[1])
                csets[u] = set()
                fmt = fmt.replace(ss,'{' + ss + '}', 1)
                ulst += [u]

            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.cell:
                    cu = c.get_u()
                    if cu == None:
                        cu = 0
                    if cu in csets.keys():
                        csets[cu].add(c.name)
                elif c.ctype == mp.CID.surface:
                    break

            farg = {}
            for k, v in csets.items():
                farg['u' + str(k)] = ' '.join(map(str, rin.shorten(sorted(v))))

            # Tally card
            print fmt.format(**farg)

            # SD card. Requires tally number and number of cells
            nt = fmt.split(':')[0][1:]
            nc = len(csets[ulst[0]]) # number of cells
            print 'sd{} 1 {}r'.format(nt, nc - 1)
            print 'fc{} '.format(nt),
            for u in ulst:
                print len(csets[u]), 
            print


        elif args.mode == 'addgeom':
            # add stuff to geometry definition of cells.

            # Get info from the --map file:
            extr = {}
            rem = set()
            if ',' in args.m :
                ds1, ds2 = args.m.split(',')
            else:
                ds1 = ''
                ds2 = ''
            if args.map:
                for l in open(args.map):
                    l = l.strip()
                    if l:
                        tokens = l.split(None, 1)
                        if len(tokens) == 1:
                            # special case: cell c should be removed from the resulting input.
                            rem.add(int(tokens[0]))
                        else:
                            c, s = tokens
                            c = int(c)
                            if ',' in s:
                                s1, s2 = s.split(',')
                                s1 = ' ' + s1.strip() + ' '
                                s2 = ' ' + s2.strip() + ' '
                            else:
                                s1 = ' ' + s.strip() + ' '
                                s2 = ''
                            extr[c] = (s1, s2)
    
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    c.geom_prefix = ds1
                    c.geom_suffix = ds2
                    if c.name in extr.keys():
                        s1, s2 = extr[c.name]
                        c.geom_prefix = s1
                        c.geom_suffix = s2
                    if c.name not in rem:
                        print c.card(),
                else:
                    print c.card(), 

        elif args.mode == 'merge':
            # Merge treats models as the main one and an additional one.
            # Title of the resulting model -- from the main model, or user specified by -t option.
            # Blocks of the additional model are denoted by user-specified comments, or by "c numjuggler title"

            # get cards of the second input
            cards2 = list(mp.get_cards(args.m, debuglog))

            blk1 = mp.get_blocks(cards)
            blk2 = mp.get_blocks(cards2)

            # The first input is used as the main one.  Blocks of the second input are inserted at the end,
            # surrounded by comments.

            # Message -- from the 1-st input if exists, otherwise -- from the second.
            if mp.CID.message in blk1.keys():
                mb = blk1[mp.CID.message]
            elif mp.CID.message in blk2.keys():
                mb = blk2[mp.CID.message]
            else:
                mb = []
            if mb:
                for c in mb:
                    print c.card(),
                print ''

            # Title:
            if args.t == "0":
                # default one. Use title of the main input
                t = blk1[mp.CID.title][0].card()[:-1]
            else:
                t = args.t
            print t

            # Comments, denoting blocks of the additional model:
            if args.c == "0":
                # default. Use the additional model's title
                t2 = blk2[mp.CID.title][0]  # Assumed that both inputs have title cards, i.e. not continuation input files.
                cmnt = 'c {} {} cards ' + '"{}"'.format(t2.card()[:-1])         # emphasize second title
            else:
                cmnt = 'c {} {} cards ' + args.c

            ## # Title -- from the 1-st input, and add comment about merging
            ## t1 = blk1[mp.CID.title][0]
            ## t2 = blk2[mp.CID.title][0]  # Assumed that both inputs have title cards, i.e. not continuation input files.
            ## t2 = '"{}"'.format(t2.card()[:-1])         # emphasize second title
            ## print t1.card(),

            ## # The original title card is followed by user-specified message. If no, by the title of the 2-nd input:
            ## if args.c == '0':
            ##     comment = t2
            ## else:
            ##     comment = repr(args.c)

            ## print 'c numjuggler merged with {}'.format(t2)

            # Cells, surfaces and data:
            for t in [mp.CID.cell, mp.CID.surface, mp.CID.data]:
                for c in blk1[t]:
                    print c.card(),

                if t in blk2.keys() and blk2[t]:
                    # First check if blk2 actually contains any cards:
                    flg = False
                    for c in blk2[t]:
                        if c.ctype == t: 
                            flg = True
                            break
                    if flg:
                        # print 'c numjuggler: start {} block from {}'.format(mp.CID.get_name(t), t2)
                        print cmnt.format('start', mp.CID.get_name(t))
                        for c in blk2[t]:
                            print c.card(),
                        # print 'c numjuggler: end {} block from {}'.format(mp.CID.get_name(t), t2)
                        print cmnt.format('end', mp.CID.get_name(t))

                if t != mp.CID.data: 
                    # do not add empty line after data block
                    print ''

        elif args.mode == 'uexp':
            if args.u == "0":
                N = " u=0 "
            else:
                N = args.u

            # Define function that filters cells to be checked:
            if args.c == "0":
                # default. Check all cells.
                cfunc = lambda n: True
            elif "!" in args.c:
                # Check only cells not mentioned in -c
                cset = set(rin.expand(args.c.replace("!", " ").split()))
                cfunc = lambda n: n not in cset
            else:
                # Check only cells  mentioned in -c
                cset = set(rin.expand(args.c.replace("!", " ").split()))
                cfunc = lambda n: n in cset

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    if cfunc(c.name) and 'u' not in map(lambda t: t[1], c.values):
                        c.input[-1] += N # ' u=0'
                print c.card(),

        elif args.mode == 'wrap':
            for c in cards:
                print c.card(True),

        elif args.mode == 'rems':
            for c in cards:
                c.remove_spaces()
                print c.card(),

        elif args.mode == 'remc':
            for c in cards:
                if c.ctype == mp.CID.comment:
                    continue
                print c.card(),

        elif args.mode == 'split':
            # # old approach:
            # # split input file into blocks
            # fp = {}
            # fp[mp.CID.message] = open(args.inp + '.1message', 'w')
            # fp[mp.CID.title]   = open(args.inp + '.2title', 'w')
            # fp[mp.CID.cell]    = open(args.inp + '.3cells', 'w')
            # fp[mp.CID.surface] = open(args.inp + '.4surfaces', 'w')
            # fp[mp.CID.data]    = open(args.inp + '.5data', 'w')
            # cct = cards[0].ctype
            # cmnt = None
            # for c in cards:
            #     # blank line is attached to the end of block.
            #     # Comment is printed before the next card.
            #     if c.ctype > 0:
            #         # where to print is defined by card ctype:
            #         fff = fp[c.ctype]
            #     if c.ctype == mp.CID.comment:
            #         # remember comment to print before next meaningful card
            #         cmnt = c
            #     else:
            #         if cmnt:
            #             print >> fff, cmnt.card(),
            #             cmnt = None
            #         if c.ctype != mp.CID.blankline:
            #             # do not print blank lines
            #             print >> fff, c.card(),
            # # do not forget the last comment
            # if cmnt:
            #     print >> fff, cmnt.card(),


            # for fff in fp.values():
            #     fff.close()

            # new approach:

            blocks = mp.get_blocks(cards)
            for k, cl in blocks.items():
                if cl:
                    i = mp.CID.get_name(k)
                    with open(args.inp + '.{}{}'.format(k, i), 'w') as fout:
                        for c in cl:
                            print >> fout, c.card(),

        elif args.mode == 'matan':
            # Compare pairwise mateiral cards. Two materials are compared by
            # their string representation

            from pirs.mcnp import Material
            # read all material cards and convert to string representation
            sd = {} 
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.data and c.dtype == 'Mn':
                    m = Material.parseCard(c)
                    m.remove_duplicates()
                    m.normalize(1.0)
                    s = m.card(sort=True, suffixes=False, comments=False)
                    if s not in sd.keys():
                        sd[s] = [m.name]
                    else:
                        sd[s].append(m.name)

            # analyse material cards:
            i = 1
            for s, m in sd.items():
                print i, m 
                i += 1


        elif args.mode == 'mdupl':
            # remove duplicate material cards, if they are equal.

            mset = set()
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.data and c.dtype == 'Mn':
                    if c.values[0][0] not in mset:
                        print c.card(),
                        mset.add(c.values[0][0])
                else:
                    print c.card(),

        elif args.mode == 'sdupl':
            # report duplicate (close) surfaces.
            # dict of unique surafces
            us = {}

            #  surface types coefficients that can only be proportional
            pcl =  {
                    'p': (0,),
                    'sq': (0, 7),
                    'gq': (0,)
                    }
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.surface:
                    # compare this surface with all previous and if unique, add to dict
                    # print '--surface', c.card(),
                    ust = us.get(c.stype, {})
                    if ust == {}:
                        us[c.stype] = ust
                    for sn, s in ust.items():
                        if s.stype == c.stype:
                            # current surface card and s have the same type. Compare coefficients:
                            if mp.are_close_lists(s.scoefs, c.scoefs, pci=pcl.get(c.stype, [])):
                                print c.card(comment=False)
                                print s.card(comment=False)
                                print 
                                # print 'is close to {}'.format(sn)
                                break
                    else:
                        # add c to us:
                        cn = c.values[0][0]  # surface name
                        ust[cn] = c
                        # print 'is unique'

        elif args.mode == 'msimp':
            # simplify material cards
            for c in cards:
                if c.ctype == mp.CID.data:
                    c.get_values()
                    if c.dtype == 'Mn':
                        inp = []
                        inp.append(c.input[0].replace('} ', '} 1001 1.0 $ msimpl ', 1))
                        for i in c.input[1:]:
                            inp.append('c msimpl ' + i)
                        c.input = inp
                print c.card(),

        elif args.mode == 'remu':
            if args.u[0] == '!':
                # -u option starts with !. In this case, remove all other universes.
                iflag = True
                args.u = args.u[1:]
            else:
                iflag = False
            uref = set(map(int, args.u.split()))
            cset = set()
            sset = set()
            mset = set()
            if args.map != '':
                # read cells to remove from --map file
                for l in open(args.map):
                    for v in l.split():
                        cset.add(int(v))
            if args.c != '0':
                le = rin.expand(args.c.split())
                for v in le:
                    cset.add(int(v))

            # get card values
            uset = set() # in case universes require inversion
            for c in cards:
                if c.ctype in (mp.CID.cell, mp.CID.surface, mp.CID.data):
                    c.get_values()
                    uset.add(c.get_u())
            if iflag:
                uref = uset.difference(uref)

            # get list of cells to be removed
            # and list of surfaces to be preserved
            for c in cards:
                if c.ctype == mp.CID.cell:
                    if c.get_u() in uref:
                        cset.add(c.name)
                    elif c.name not in cset:
                        # collect surfaces needed for other cells
                        for v, t in c.values:
                            if t == 'sur':
                                sset.add(v)
                            if t == 'mat':
                                mset.add(v)

            for c in cards:
                if c.ctype == mp.CID.cell and c.name in cset:
                    pass
                elif c.ctype == mp.CID.surface and c.name not in sset:
                    pass
                elif c.ctype == mp.CID.data and c.dtype == 'Mn' and c.values[0][0] not in mset:
                    print 'c qqq', repr(c.values[0][0])
                    pass
                else:
                    # check that cell card does not depend on one of cset:
                    if c.get_refcells():
                        for i in range(len(c.values)):
                            v, t = c.values[i]
                            if t == 'cel' and v in cset:
                                c.values[i] = ('___', 'cel')

                    print c.card(),
            print 'c sset', ' '.join(map(str, rin.shorten(sorted(sset))))
            print 'c mset', ' '.join(map(str, rin.shorten(sorted(mset))))

        elif args.mode == 'zrotate':
            
            from pirs.core.trageom import Vector3, pi
            ag = float(args.c)    # in grad
            ar = ag * pi / 180.   # in radians

            # new transformation number:
            trn = args.t 
            trcard = '*tr{} 0 0 0 {} {} 90   {} {} 90   90 90 0'.format(trn, ag, ag-90, 90+ag, ag)
            # change all tr cards and surface cards:
            for c in cards:
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    # Surface parameters are not parsed, only surface number and transformation.
                    if len(c.values) == 1:
                        # surface has no transformation. Add the new one
                        inpt = '\n'.join(c.input)
                        inpt = inpt.replace('} ', '} ' + trn + ' ', 1)
                        c.input = inpt.split('\n')

                if c.ctype == mp.CID.data:
                    c.get_values()
                    if c.dtype == 'TRn':
                        # put new tr card just before the 1-st tr card in the input:
                        if trcard:
                            print trcard
                            trcard = None
                        # apply changes, assuming that tr card contains all 12 entries:
                        o = Vector3(car=map(lambda v: v[0], c.values[1:4]))
                        o.t += ar
                        c.values[1] = (o.x, 'float')
                        c.values[2] = (o.y, 'float')
                        c.values[3] = (o.z, 'float')
                        if c.unit == '':
                            # rotation matrix contains cos
                            b1 = Vector3(car=map(lambda v: v[0], c.values[4:7]))
                            b2 = Vector3(car=map(lambda v: v[0], c.values[7:10]))
                            b3 = Vector3(car=map(lambda v: v[0], c.values[10:13]))
                            b1.t += ar
                            b2.t += ar
                            b3.t += ar
                            c.values[4] = (b1.x, 'float')
                            c.values[5] = (b1.y, 'float')
                            c.values[6] = (b1.z, 'float')
                            c.values[7] = (b2.x, 'float')
                            c.values[8] = (b2.y, 'float')
                            c.values[9] = (b2.z, 'float')
                            c.values[10] = (b3.x, 'float')
                            c.values[11] = (b3.y, 'float')
                            c.values[12] = (b3.z, 'float')
                        else:
                            # rotation matrix contains angles in grad.
                            b1, b2, b3, b4, b5, b6, b7, b8, b9 = map(lambda v: v[0], c.values[4:13])

                            # Assume that it already describes rotation around z axis
                            assert b3 == 90 and b6 == 90 and b7 == 90 and b8 == 90 and b9 == 0

                            b1 += ag
                            b2 += ag
                            b4 += ag
                            b5 += ag
                            c.values[4] = (b1, 'float')
                            c.values[5] = (b2, 'float')
                            c.values[7] = (b4, 'float')
                            c.values[8] = (b5, 'float')

                print c.card(), 

        
        elif args.mode == 'annotate':
            # Read text from map file, add "c" to each line and put after the title.
            if args.c == "0":
                # default commenting string:
                cs = 'c '
            else:
                # user-specified commenting string:
                cs = args.c

            txt = map( lambda l: cs + l, open(args.map).readlines())

            for c in cards:
                print c.card(),
                if c.ctype == mp.CID.title:
                    for l in txt:
                        print l,   # readlines() method returns lines with \n at the end


        elif args.mode == 'getc':
            # Extract comments that take more than 10 lines:
            if args.c != "0":
                N = int(args.c)
            else:
                N = 10

            for c in cards:
                if c.ctype == mp.CID.comment:
                    ccc = c.card()
                    l = len(ccc.splitlines())
                    if l >= N:
                        print c.pos, l
                        print ccc,

        elif args.mode == 'extr':
            # extract cell specified in -c keyword and necessary materials, and surfaces.
            cset = set()
            flag = '' # can be '!'
            if args.c != '0':
                if '!' in args.c:
                    args.c = args.c.replace('!', ' ')
                    flag = '!'
                le = rin.expand(args.c.split())
                cset = set(le)
            if args.map != '':
                # cset = set()
                for l in open(args.map, 'r'):
                    for c in l.split():
                        cset.add(int(c))
            # get set of all cells:
            aset = set()
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.cell:
                    aset.add(c.name)

            if args.u != '0':
                uref = int(args.u)
                for c in cards:
                    if c.ctype == mp.CID.cell and c.get_u() == uref:
                        cset.add(c.name)

            # '!' means that the specified cells should NOT be extracted, but all other.
            if flag == '!':
                cset = aset.difference(cset)
            if not cset:
                print "No cells to extract are specified"
                raise Exception


            # first, get all surfaces needed to represent the cn cell.
            sset = set() # surfaces
            mset = set() # material
            tset = set() # transformations
            uset = set() # universes that fill cells of cset
            fset = set() # universes that the cells of cset belong to.
            Uset = set() # set of universes, parets belong to.
            pset = set() # parent cells, i.e. cells that are filled with universes from fset.

            # first run through cards: define filling
            for c in cards:
                if c.ctype == mp.CID.cell: 
                    if c.name in cset:
                        if c.get_f() is not None:
                            uset.add(c.get_f())
                        if c.get_u() is not None:
                            fset.add(c.get_u())

            # next runs: find all other cells:
            again = True
            while again:
                again = False
                for c in cards:
                    if c.ctype == mp.CID.cell: 
                        if c.get_u() in uset:
                            cset.add(c.name)
                            if c.get_f() is not None:
                                if c.get_f() not in uset:
                                    uset.add(c.get_f())
                                    again = True
                        if c.name in cset:
                            cref = c.get_refcells() 
                            if cref.difference(cset):
                                again = True
                                cset = cset.union(cref)
                        if c.get_f() in fset:
                            # this cell is parent of one of cset.
                            pset.add(c.name)
                            if c.get_u() not in Uset:
                                again = True
                                Uset.add(c.get_u())
                        if c.get_u() in Uset:
                            if c.get_f() not in fset:
                                c.get_f(newv=0)
                            pset.add(c.name)

            # final run: for all cells find surfaces, materials, etc.                    
            cset = cset.union(pset)
            for c in cards:
                if c.ctype == mp.CID.cell and c.name in cset:
                    # get all surface names and the material, if any.
                    for v, t in c.values:
                        if t == 'sur':
                            sset.add(v)
                        elif t == 'mat':
                            mset.add(v)
                        elif t == 'tr':
                            tset.add(v)

                if c.ctype == mp.CID.surface and c.name in sset:
                    # surface card can refer to tr
                    for v, t in c.values:
                        if t == 'tr':
                            tset.add(v)

            blk = None
            for c in cards:
                if c.ctype == mp.CID.title:
                    print c.card(),
                if c.ctype == mp.CID.cell and c.name in cset:
                    print c.card(),
                    blk = c.ctype
                if c.ctype == mp.CID.surface:
                    if blk == mp.CID.cell:
                        print
                        blk = c.ctype
                    if  c.name in sset:
                        print c.card(),
                if c.ctype == mp.CID.data :
                    if blk != c.ctype:
                        print
                        blk = c.ctype
                    if c.dtype == 'Mn' and c.values[0][0] in mset:
                        print c.card(),
                    if c.dtype == 'TRn':#  and c.values[0][0] in tset:
                        print c.card(),
        
        elif args.mode == 'nogq':
            from numjuggler import nogq
            try:
                # try because nogq requires numpy.
                from numjuggler import nogq
            except ImportError:
                print "Numpy package is required for --mode nogq but cannot be found. Install it with "
                print ""
                print " > pip install numpy"
                raise
            except:
                raise

            trn0 = int(args.t)
            cflag = False if args.c == "0" else True

            vfmt = ' {:15.8e}'*3
            tfmt = 'tr{} 0 0 0 ' + ('\n     ' + vfmt)*3
            trd = {} 
            # replace GQ cylinders with c/x + tr 
            for c in cards:
                crd = c.card()
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    if c.stype == 'gq':
                        p = nogq.get_gq_params(' '.join(c.input))
                        a2, g, k = nogq.get_k(p)
                        if cflag:
                            crd = crd[:-1] + '$ a^2={:12.6e} c={:12.6e}\n'.format(a2, g + a2)
                        if abs((g + a2) / a2) < 1e-6:
                            # this is a cylinder. Comment original card and write another one
                            R, x0, i, j = nogq.cylinder(p, a2, g, k)                            
                            # add transformation set
                            tr = tuple(i) + tuple(j) + tuple(k) 
                            for k, v in trd.items():
                                if tr == v:
                                    trn = k
                                    break
                            else:
                                trn = len(trd) + 1
                                trd[trn] = tr
                            # replace surface card
                            if cflag:
                                crd = 'c ' + '\nc '.join(c.card().splitlines()) + '\n'
                            else:
                                crd = ''
                            crd += '{} {} c/z {:15.8e} 0 {:15.8e}\n'.format(c.name, trn + trn0, x0, R)
                print crd,
                if trd and c.ctype == mp.CID.blankline:
                    # this is blankline after surfaces. Put tr cards here
                    for k, v in sorted(trd.items()):
                        ijk = (k + trn0,) + v 
                        print tfmt.format(*ijk)
                    trd = {}

        elif args.mode == 'count':
            # take the maximal number of surfaces from -s:
            Nmax = int(args.s) 
            if Nmax == 0:
                Nmax = 100 # default max value.
            print ('{:>10s}'*5).format('Cell', 'Line', 'all', 'unique', '>{}'.format(Nmax))
            sc = 0 # cell counter
            sa = 0 # all surfaces counter
            su = 0 # unique surface counter
            ma = 0 # maximal number of all surfaces
            mu = 0 # maximal number of unique surfaces
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    # get list of surfaces used in the cell:
                    los = []
                    for v, t in c.values:
                        if 'sur' in t:
                            los.append(v)

                    # output number of surfaces:
                    a = len(los)       # number of all surfaces
                    u = len(set(los))  # number of unique surfaces
                    print ('{:>10d}'*4).format(c.name, c.pos, a, u),
                    if a > Nmax:
                        print ' *'
                    else:
                        print ' '
                    sc += 1
                    sa += a
                    su += u
                    ma = max(ma, a)
                    mu = max(mu, u)
            print 
            print 'sum', ('{:>10d}'*3).format(sc, sa, su)
            print 'max', ('{:>10d}'*3).format(00, ma, mu)

        elif args.mode == 'nofill':
            # remove all fill= keywords from cell cards. 
            print ' Mode --mode nofill is not implemented yet.'

            # First loop: find and remove all FILL keywords. Store universes for the second loop.
            uset = set()
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()

                    for v, t in c.values:
                        if t == 'fill':
                            uset.add(v)
                            c.remove_fill()
                            break
                print c.card(), 

            print 'Universes used for FILL:', uset


        elif args.mode == 'matinfo':
            # for each material used in cell cards, output list of cells together with density and universe.
            res = {}
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    m = c.get_m()
                    d = c.get_d()
                    u = c.get_u()
                    l = res.get(m, [])
                    if not l:
                        res[m] = l
                    l.append((c.name, d, u))
                if c.ctype == mp.CID.surface:
                    break

            # print out information 
            fmt = ' '*8 + '{:>16}'*3
            print fmt.format('Cell', 'density', 'universe')
            for m in sorted(res.keys()):
                uset = set()
                for c, d, u in res[m]:
                    uset.add(u)
                print 'm{} -------------- {} {}'.format(m, len(uset), sorted(uset))

                for c, d, u in res[m]:
                    print fmt.format(c, d, u)

        elif args.mode == 'uinfo':
            # for each universe return list of its cells.
            res = {}

            # flag to sort cells in the output list:
            sflag = False if args.s == "0" else True
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    u = c.get_u()
                    u = 0 if u is None else u
                    l = res.get(u, [])
                    if not l:
                        res[u] = l
                    l.append(c.name)
                elif c.ctype == mp.CID.surface:
                    break
            # print out 
            if args.u == '0':
                for u, l in sorted(res.items()):
                    if sflag:
                        l = sorted(l)
                    print 'u{}'.format(u),
                    for e in rin.shorten(l):
                        print e,
                    print
                    print len(l)
            else:
                uref = int(args.u)
                l = res[uref]
                if sflag:
                    l = sorted(l)
                for e in rin.shorten(l):
                    print e, 


        elif args.mode == 'impinfo':

            if args.m == '0':
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        c.get_values()
                        i = c.get_imp()
                        if 0 in i.values():
                            print c.card(),
            else:
                nv = {}
                for t in args.m.split():
                    # form of args.m: "n1.0 p0 e0"
                    nv[t[0]] = float(t[1:])
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        c.get_values()
                        c.get_imp(nv)
                    print c.card(),


        elif args.mode == 'sinfo':
            # first, get the list of surfaces:
            sl = {}
            st = set() # set of used surface types
            for c in cards:
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    sl[c.name] = (set(), c.stype)
                    st.add(c.stype)
            # for each surface return list of cells:
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    for v, t in c.values:
                        if t == 'sur':
                            sl[v][0].add(c.name)
            # print out:
            for s, (cs, t) in sorted(sl.items()):
                print s, t, sorted(cs)
            for s in sorted(st):
                print s

        
        elif args.mode == 'vsource':

            def print_planar(params, d=1e-5, u='0'):

                # u defines which sdef is printed:
                v = 1
                if '_' in u:
                    v = -1
                    u = u.replace('_', '')
                elif '+' in u:
                    v = 1
                    u = u.replace('+', '')

                c = ['c x', 'c y', 'c z']
                if u in 'xX':
                    c[0] = '  '
                elif u in 'yY':
                    c[1] = '  '
                elif u in 'zZ':
                    c[2] = '  '
                x1, x2, y1, y2, z1, z2 = params[:]
                dx = x2 - x1
                dy = y2 - y1
                dz = z2 - z1
                mx = (x1 + x2)*0.5
                my = (y1 + y2)*0.5
                mz = (z1 + z2)*0.5
                xs =  mx - (dx*0.5 - d)*v
                ys =  my - (dy*0.5 - d)*v
                zs =  mz - (dz*0.5 - d)*v
                if u in 'xX':
                    fmt = 'sdef x {:12} y d2  z d3  vec {} dir 1 wgt {}'
                    print fmt.format(xs, '{} 0 0'.format(v), dz*dy)
                elif u in 'yY':
                    fmt = 'sdef y {:12} x d1  z d3  vec {} dir 1 wgt {}'
                    print fmt.format(ys, '0 {} 0'.format(v), dx*dz)
                elif u in 'zZ':
                    fmt = 'sdef z {:12} x d1  y d2  vec {} dir 1 wgt {}'
                    print fmt.format(zs, '0 0 {}'.format(v), dx*dy)

                fm2 = 'si{:1} h {:12} {:12} $ {} {}'
                print fm2.format(1, x1 + d, x2 - d, dx, mx)
                print fm2.format(2, y1 + d, y2 - d, dy, my)
                print fm2.format(3, z1 + d, z2 - d, dz, mz)
                fm3 = 'sp{:1} d 0 1'
                print fm3.format(1)
                print fm3.format(2)
                print fm3.format(3)

            def print_spherical(params, d=1e-5):
                print 'Not implemented yet'

            if args.c != '0':
                print 'c source from -c parameters'
                vals = map(float, args.c.split())
                if len(vals) == 1:
                    # radius of a sphere on the origin
                    print_spherical([0, 0, 0, vals[0]])
                elif len(vals) == 4:
                    # sphere coordinates and radius:
                    print_spherical(vals)
                elif len(vals) == 6:
                    # x, y and z range of a box:
                    print_planar(vals, u=args.u)
                else:
                    raise ValueError('Wrong number of entries in the -c option')

            if args.s != '0':
                print 'c source from -s parameters'
                nset = set(map(int, args.s.split()))
                sset = {}
                for c in cards:
                    if c.ctype == mp.CID.surface:
                        c.get_values()
                        if c.name in nset:
                            sset[c.name] = c
                    elif c.ctype == mp.CID.data:
                        break

                if len(sset) == 1:
                    # -s interpreted as a sphere surface.
                    n, c = sset.items()[0]
                    if c.stype == 'so':
                        r = c.scoefs[0]
                        x = 0
                        y = 0
                        z = 0
                    elif c.stype == 's':
                        x, y, z, r = c.scoefs
                    else:
                        raise ValueError('Surface {} not a sphere'.format(n))
                    print_spherical([x, y, z, r])

                elif len(sset) == 6:
                    # -s is interpreted as a list of px, py and pz planes.
                    x = []
                    y = []
                    z = []
                    for n, c in sset.items():
                        if c.stype == 'px':
                            x.append(c.scoefs[0])
                        elif c.stype == 'py':
                            y.append(c.scoefs[0])
                        elif c.stype == 'pz':
                            z.append(c.scoefs[0])
                        else:
                            raise ValueError('Surface {} not a px, py or pz plane'.format(n))
                    print_planar(sorted(x) + sorted(y) + sorted(z), u=args.u)
                else:
                    raise ValueError('Wront number of surfaces in -s option')


        elif args.mode == 'fillempty':
            # add 'FILL =' to all void non-filled cells.
            # N = ' fill={} '.format(args.u)
            N = args.u
            M = int(args.m)
            cll = [] # list of cell lists to be filled with new u
            fl = []  # list of new u that fills cells from cll
            if args.map != '':
                # read from map list of cells where to insert the fill card
                for l in open(args.map):
                    if ':' in l:
                        # l contains cell numbers and its filling
                        s1, s2 = l.split(':')
                        cll.append( rin.expand(s1.split()) )
                        fl.append(s2)
                    else:
                        cll.append( rin.expand(l.split()))
                        fl.append(N)
            if args.c != '0':
                cll.append(rin.expand(args.c.split()))
                fl.append(N)

            # put cll and fl into a single dict:
            dll = {}
            if cll:
                for cl, f in zip(cll, fl):
                    for c in cl:
                        dll[c] = f

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    if dll:
                        if c.name in dll.keys():
                            c.input[-1] += dll[c.name] 
                    else:                        
                        m = c.get_m()
                        f = c.get_f()
                        imp = c.get_imp()
                        if imp['imp:n'] > 0 and m == M and f in [0, None]:
                            c.input[-1] += N 
                print c.card(),

        elif args.mode == 'renum':
            for c in cards:
                c.get_values()

            if args.map:
                # if map file is given, ignore all -c, -s, -u and -m.
                dm = mn.read_map_file(args.map)

            else:
                # number: index dictionary only if needed:
                if 'i' in (args.c, args.s, args.m, args.u):
                    di = mn.get_indices(cards)
                else:
                    di = {}


                dm = {}
                for t in ['cel', 'sur', 'mat', 'u', 'tr']:
                    dn = getattr(args, t[0])
                    if dn == 'i':
                        dm[t] = [None, di[t]] # None to raise an error, when None will be added to an int. (Indexes should be defined to all numbers, thus the default mapping should not be used.
                    else:
                        dm[t] = [int(dn), [(0, 0, 0)]] # do not modify zero material

            mapping = mn.LikeFunction(dm, args.log!='')

            for c in cards:
                c.apply_map(mapping)
                print c.card(),

            if args.log != '':
                mapping.write_log_as_map(args.log)


if __name__ == '__main__':
    main()

