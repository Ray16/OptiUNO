* GAMS-model aljazzaf.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 50.005000000000003 * power((x('1')) + 1, 2) + 
0.010000000000005116 * power((x('2')) - 1, 2) + 
100 * power((x('3')) - 0.5, 2);


con1.. -x('3') + 
10000 * power((x('2')) - 1, 2) + 
5000.5 * power(x('1'), 2) =e= -1;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


