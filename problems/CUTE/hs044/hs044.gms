* GAMS-model hs044.dag.gms written by dag2gams Converter at 29/03/2004 16:59:09
* University of Vienna
$offdigit;
 Set i/1*6/;
 Set j/1*4/;
 Equations objcon
con1
con2
con3
con4
con5
con6
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('1') - 
x('2') - 
x('3') - 
x('1') * x('3') + 
x('1') * x('4') + 
x('2') * x('3') - 
x('2') * x('4');


con1..x('3') + 
x('4') =l= 5;
con2..x('3') + 
2 * x('4') =l= 8;
con3..2 * x('3') + 
x('4') =l= 8;
con4..3 * x('1') + 
4 * x('2') =l= 12;
con5..4 * x('1') + 
x('2') =l= 12;
con6..x('1') + 
2 * x('2') =l= 8;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


