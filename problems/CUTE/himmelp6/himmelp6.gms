* GAMS-model himmelp6.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*5/;
 Set j/1*2/;
 Equations objcon
con1
con2
con3
con4
con5
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 28.1064434908 * (1/(x('2') + 
1)) + 
2.8673112392000002 * exp(0.00050000000000000001 * x('1') * x('2')) + 
3.8112755343 * x('1') + 
6.8306567613000002 * x('2') - 
0.12693663450000001 * power(x('1'), 2) - 
0.25645812530000001 * power(x('2'), 2) + 
0.0020567665 * power(x('1'), 3) + 
0.0034604029999999999 * power(x('2'), 3) - 
1.0345e-05 * power(x('1'), 4) - 
1.3513899999999999e-05 * power(x('2'), 4) - 
power(x('2'), 2) * (0.00034054620000000002 * x('1') - 
5.2375000000000003e-06 * power(x('1'), 2) - 
6.3000000000000002e-09 * power(x('1'), 3)) - 
x('2') * (0.030234479299999999 * x('1') - 
0.0012813448000000001 * power(x('1'), 2) + 
3.5259899999999998e-05 * power(x('1'), 3) - 
2.266e-07 * power(x('1'), 4)) - 
power(x('2'), 3) * ((-1.6638000000000001e-06) * x('1') + 
6.9999999999999996e-10 * power(x('1'), 3)) - 75.196366667700005;


con1..-x('1') + 
0.16 * x('2') =l= 41.399999999999999;
con2..x('1') - 
1.5 * x('2') =l= 22.5;
con3..5 * x('1') + 
100 * x('2') - 
power(x('2'), 2) =l= 2775;
con4..-x('2') + 
0.0080000000000000002 * power(x('1'), 2) =l= 0;
con5..x('1') * x('2') =g= 700;
x.lo('1')=0;
x.up('1')=75;
x.lo('2')=0;
x.up('2')=65;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


