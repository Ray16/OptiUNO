* GAMS-model chnrosnb.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set j/1*50/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('2')) - 1, 2) + 
power((x('3')) - 1, 2) + 
power((x('4')) - 1, 2) + 
power((x('5')) - 1, 2) + 
power((x('6')) - 1, 2) + 
power((x('7')) - 1, 2) + 
power((x('8')) - 1, 2) + 
power((x('9')) - 1, 2) + 
power((x('10')) - 1, 2) + 
power((x('11')) - 1, 2) + 
power((x('12')) - 1, 2) + 
power((x('13')) - 1, 2) + 
power((x('14')) - 1, 2) + 
power((x('15')) - 1, 2) + 
power((x('16')) - 1, 2) + 
power((x('17')) - 1, 2) + 
power((x('18')) - 1, 2) + 
power((x('19')) - 1, 2) + 
power((x('20')) - 1, 2) + 
power((x('21')) - 1, 2) + 
power((x('22')) - 1, 2) + 
power((x('23')) - 1, 2) + 
power((x('24')) - 1, 2) + 
power((x('25')) - 1, 2) + 
power((x('26')) - 1, 2) + 
power((x('27')) - 1, 2) + 
power((x('28')) - 1, 2) + 
power((x('29')) - 1, 2) + 
power((x('30')) - 1, 2) + 
power((x('31')) - 1, 2) + 
power((x('32')) - 1, 2) + 
power((x('33')) - 1, 2) + 
power((x('34')) - 1, 2) + 
power((x('35')) - 1, 2) + 
power((x('36')) - 1, 2) + 
power((x('37')) - 1, 2) + 
power((x('38')) - 1, 2) + 
power((x('39')) - 1, 2) + 
power((x('40')) - 1, 2) + 
power((x('41')) - 1, 2) + 
power((x('42')) - 1, 2) + 
power((x('43')) - 1, 2) + 
power((x('44')) - 1, 2) + 
power((x('45')) - 1, 2) + 
power((x('46')) - 1, 2) + 
power((x('47')) - 1, 2) + 
power((x('48')) - 1, 2) + 
power((x('49')) - 1, 2) + 
power((x('50')) - 1, 2) + 
31.359999999999996 * power(x('1') - 
power(x('2'), 2), 2) + 
92.159999999999997 * power(x('2') - 
power(x('3'), 2), 2) + 
31.359999999999996 * power(x('3') - 
power(x('4'), 2), 2) + 
49 * power(x('4') - 
power(x('5'), 2), 2) + 
23.039999999999999 * power(x('5') - 
power(x('6'), 2), 2) + 
81 * power(x('6') - 
power(x('7'), 2), 2) + 
23.039999999999999 * power(x('7') - 
power(x('8'), 2), 2) + 
16 * power(x('8') - 
power(x('9'), 2), 2) + 
19.360000000000003 * power(x('9') - 
power(x('10'), 2), 2) + 
36 * power(x('10') - 
power(x('11'), 2), 2) + 
40.960000000000008 * power(x('11') - 
power(x('12'), 2), 2) + 
25 * power(x('12') - 
power(x('13'), 2), 2) + 
25 * power(x('13') - 
power(x('14'), 2), 2) + 
23.039999999999999 * power(x('14') - 
power(x('15'), 2), 2) + 
23.039999999999999 * power(x('15') - 
power(x('16'), 2), 2) + 
31.359999999999996 * power(x('16') - 
power(x('17'), 2), 2) + 
4 * power(x('17') - 
power(x('18'), 2), 2) + 
4 * power(x('18') - 
power(x('19'), 2), 2) + 
25 * power(x('19') - 
power(x('20'), 2), 2) + 
51.840000000000003 * power(x('20') - 
power(x('21'), 2), 2) + 
9 * power(x('21') - 
power(x('22'), 2), 2) + 
25 * power(x('22') - 
power(x('23'), 2), 2) + 
31.359999999999996 * power(x('23') - 
power(x('24'), 2), 2) + 
40.960000000000008 * power(x('24') - 
power(x('25'), 2), 2) + 
64 * power(x('25') - 
power(x('26'), 2), 2) + 
16 * power(x('26') - 
power(x('27'), 2), 2) + 
40.960000000000008 * power(x('27') - 
power(x('28'), 2), 2) + 
25 * power(x('28') - 
power(x('29'), 2), 2) + 
121 * power(x('29') - 
power(x('30'), 2), 2) + 
25 * power(x('30') - 
power(x('31'), 2), 2) + 
25 * power(x('31') - 
power(x('32'), 2), 2) + 
25 * power(x('32') - 
power(x('33'), 2), 2) + 
144 * power(x('33') - 
power(x('34'), 2), 2) + 
36 * power(x('34') - 
power(x('35'), 2), 2) + 
64 * power(x('35') - 
power(x('36'), 2), 2) + 
25 * power(x('36') - 
power(x('37'), 2), 2) + 
31.359999999999996 * power(x('37') - 
power(x('38'), 2), 2) + 
51.840000000000003 * power(x('38') - 
power(x('39'), 2), 2) + 
36 * power(x('39') - 
power(x('40'), 2), 2) + 
77.440000000000012 * power(x('40') - 
power(x('41'), 2), 2) + 
31.359999999999996 * power(x('41') - 
power(x('42'), 2), 2) + 
36 * power(x('42') - 
power(x('43'), 2), 2) + 
25 * power(x('43') - 
power(x('44'), 2), 2) + 
64 * power(x('44') - 
power(x('45'), 2), 2) + 
36 * power(x('45') - 
power(x('46'), 2), 2) + 
25 * power(x('46') - 
power(x('47'), 2), 2) + 
31.359999999999996 * power(x('47') - 
power(x('48'), 2), 2) + 
5.7599999999999998 * power(x('48') - 
power(x('49'), 2), 2) + 
36 * power(x('49') - 
power(x('50'), 2), 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


