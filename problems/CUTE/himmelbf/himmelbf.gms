* GAMS-model himmelbf.dag.gms written by dag2gams Converter at 29/03/2004 16:59:07
* University of Vienna
$offdigit;
 Set j/1*4/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 10000 * power((0.089445438282647588 * ((power(x('1'), 2) + 
0.000428 * power(x('2'), 2) + 
1.8318400000000001e-07 * power(x('3'), 2)) / ((0.000428 * power(x('4'), 2) + 
1)))) - 1, 2) + 
10000 * power((0.060827250608272501 * ((power(x('1'), 2) + 
0.001 * power(x('2'), 2) + 
9.9999999999999995e-07 * power(x('3'), 2)) / ((0.001 * power(x('4'), 2) + 
1)))) - 1, 2) + 
10000 * power((0.061728395061728399 * ((power(x('1'), 2) + 
0.0016100000000000001 * power(x('2'), 2) + 
2.5921000000000001e-06 * power(x('3'), 2)) / ((0.0016100000000000001 * power(x('4'), 2) + 
1)))) - 1, 2) + 
10000 * power((0.04504504504504505 * ((power(x('1'), 2) + 
0.0020899999999999998 * power(x('2'), 2) + 
4.3680999999999997e-06 * power(x('3'), 2)) / ((0.0020899999999999998 * power(x('4'), 2) + 
1)))) - 1, 2) + 
10000 * power((0.041631973355537054 * ((power(x('1'), 2) + 
0.00348 * power(x('2'), 2) + 
1.21104e-05 * power(x('3'), 2)) / ((0.00348 * power(x('4'), 2) + 
1)))) - 1, 2) + 
10000 * power((0.031928480204342274 * ((power(x('1'), 2) + 
0.0052500000000000003 * power(x('2'), 2) + 
2.7562500000000002e-05 * power(x('3'), 2)) / ((0.0052500000000000003 * power(x('4'), 2) + 
1)))) - 1, 2) + 
10000 * power((0.13529968881071575 * power(x('1'), 2)) - 1, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


