* GAMS-model hs072.dag.gms written by dag2gams Converter at 29/03/2004 16:59:09
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*4/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('1') + 
x('2') + 
x('3') + 
x('4') + 1;


con1..0.16 * (1/x('1')) + 
0.35999999999999999 * (1/x('2')) + 
0.64000000000000001 * (1/x('3')) + 
0.64000000000000001 * (1/x('4')) =l= 0.010085;
con2..4 * (1/x('1')) + 
2.25 * (1/x('2')) + 
1/x('3') + 
0.25 * (1/x('4')) =l= 0.040099999999999997;
x.lo('1')=0.001;
x.up('1')=400000;
x.lo('2')=0.001;
x.up('2')=300000;
x.lo('3')=0.001;
x.up('3')=200000;
x.lo('4')=0.001;
x.up('4')=100000;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


