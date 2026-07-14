* GAMS-model hs100lnp.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*7/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-10) * x('6') - 
8 * x('7') + 
power((x('1')) - 10, 2) + 
7 * power(x('6'), 2) + 
5 * power((x('2')) - 12, 2) + 
3 * power((x('4')) - 11, 2) - 
4 * x('6') * x('7') + 
power(x('3'), 4) + 
power(x('7'), 4) + 
10 * power(x('5'), 6);


con1.. (-5) * x('6') + 
11 * x('7') - 
4 * power(x('1'), 2) - 
power(x('2'), 2) - 
2 * power(x('3'), 2) + 
3 * x('1') * x('2') =e= 0;
con2.. x('3') + 
5 * x('5') + 
2 * power(x('1'), 2) + 
4 * power(x('4'), 2) + 
3 * power(x('2'), 4) =e= 127;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


