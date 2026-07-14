* GAMS-model biggsc4.dag.gms written by dag2gams Converter at 29/03/2004 16:59:09
* University of Vienna
$offdigit;
 Set i/1*13/;
 Set j/1*4/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
con10
con11
con12
con13
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(x('1') * x('3')) - 
x('2') * x('4');


con1..x('1') + 
x('2') + 
x('3') + 
x('4') =g= 5;
con2..x('3') + 
x('4') =g= 1.5;
con3..x('3') + 
x('4') =l= 6.5;
con4..x('2') + 
x('4') =g= 2;
con5..x('2') + 
x('4') =l= 7;
con6..x('2') + 
x('3') =g= 2;
con7..x('2') + 
x('3') =l= 7;
con8..x('1') + 
x('2') =g= 2.5;
con9..x('1') + 
x('2') =l= 7.5;
con10..x('1') + 
x('4') =g= 2.5;
con11..x('1') + 
x('4') =l= 7.5;
con12..x('1') + 
x('3') =g= 2.5;
con13..x('1') + 
x('3') =l= 7.5;
x.lo('1')=0;
x.up('1')=5;
x.lo('2')=0;
x.up('2')=5;
x.lo('3')=0;
x.up('3')=5;
x.lo('4')=0;
x.up('4')=5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


