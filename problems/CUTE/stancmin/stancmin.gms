* GAMS-model stancmin.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*3/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -((3 * x('1') + 
6 * x('2') + 
2 * x('3') - 
11) / (x('1') + 
4 * x('2') + 
x('3') + 
1));


con1..x('1') + 
4 * x('2') + 
x('3') =l= 1;
con2..3 * x('1') + 
4 * x('2') + 
x('3') =l= 2;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


