* GAMS-model hs061.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
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
objcon.. obj =e= 16 * x('1') - 
24 * x('2') - 
33 * x('3') + 
2 * power(x('1'), 2) + 
2 * power(x('2'), 2) + 
4 * power(x('3'), 2);


con1.. 4 * x('3') - 
power(x('2'), 2) =e= 11;
con2.. 3 * x('3') - 
2 * power(x('1'), 2) =e= 7;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


