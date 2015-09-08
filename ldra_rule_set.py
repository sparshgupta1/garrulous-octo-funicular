import os
import re
import sys



def get_ldra_rule_set():
   rule_set = {}
   
   rule_set["MISRA-C:2004"] = [ "48 S;", "12 X;", "33 X;", "74 D;", "61 S;", "567 S;", "56 S;", "26 X;", "62 X;", "429 S;", "31 X;", "480 S;", "20 S;", "40 X;", "87 D;", "286 S;", "81 S;", "72 D;", "5 X;", "63 X;", "271 S;", "248 S;", "36 D;", "54 S;", "11 S;", "120 S;", "553 S;", "63 D;", "52 X;", "496 S;", "25 X;", "52 S;", "18 D;", "270 S;", "54 X;", "1 S;", "85 S;", "95 S;", "441 S;", "15 X;", "580 S;", "69 S;", "21 S;", "46 X;", "19 X;", "126 S;", "65 S;", "442 S;", "550 S;", "493 S;", "57 S;", "69 D;", "243 S;", "344 S;", "42 X;", "27 X;", "430 S;", "42 D;", "384 S;", "293 S;", "128 S;", "338 S;", "55 X;", "7 C;", "377 S;", "127 S;", "412 S;", "20 X;", "287 S;", "341 S;", "478 S;", "10 X;", "477 S;", "70 X;", "9 X;", "62 D;", "9 S;", "487 S;", "486 S;", "58 X;", "451 S;", "92 S;", "437 S;", "7 X;", "73 S;", "30 S;", "457 S;", "47 S;", "444 S;", "337 S;", "112 S;", "62 S;", "428 S;", "373 S;", "632 S;", "389 S;", "122 S;", "130 S;", "48 X;", "49 X;", "376 S;", "14 X;", "334 S;", "1 Q;", "110 S;", "42 S;", "203 S;", "172 S;", "581 S;", "409 S;", "176 S;", "360 S;", "55 D;", "25 D;", "465 S;", "410 S;", "60 D;", "58 S;", "408 S;", "68 S;", "5 Q;", "482 S;", "16 X;", "406 S;", "36 X;", "61 X;", "64 X;", "636 S;", "60 S;", "145 S;", "77 S;", "96 S;", "1 X;", "494 S;", "2 D;", "43 X;", "103 S;", "71 S;", "426 S;", "75 S;", "590 S;", "113 S;", "13 S;", "495 S;", "156 S;", "345 S;", "436 S;", "296 S;", "125 S;", "342 S;", "374 S;", "329 S;", "4 X;", "147 S;", "134 S;", "86 S;", "219 S;", "489 S;", "99 S;", "32 S;", "29 X;", "78 S;", "407 S;", "269 S;", "439 S;", "39 S;", "36 S;", "49 S;", "41 S;", "461 S;", "34 D;", "249 S;", "11 X;", "302 S;", "385 S;", "50 X;", "438 S;", "325 S;", "30 X;", "59 X;", "403 S;", "450 S;", "41 X;", "576 S;", "80 S;", "324 S;", "72 S;", "446 S;", "435 S;", "1 U;", "94 S;", "6 X;", "17 X;", "59 S;", "77 D;", "63 S;", "53 S;", "32 X;", "589 S;", "60 X;", "131 S;", "44 S;", "136 S;", "245 S;", "72 X;", "6 D;", "22 X;", "66 S;", "91 D;", "491 S;", "43 D;", "445 S;", "50 S;", "582 S;", "554 S;", "107 S;", "114 S;", "43 S;", "28 X;", "119 S;", "67 S;", "26 D;", "83 D;", "69 X;", "8 X;", "21 X;", "24 X;", "18 X;", "27 D;", "37 S;", "101 S;", "545 S;", "382 S;", "24 D;", "143 S;", "488 S;", "397 S;", "57 X;", "17 D;", "33 D;", "340 S;", "327 S;", "573 S;", "51 X;", "443 S;", "433 S;", "35 X;", "452 S;", "88 S;", "322 S;", "35 D;", "13 X;", "102 S;", "615 S;", "139 S;", "339 S;", "481 S;", "45 X;", "110 D;", "440 S;", "292 S;", "34 X;", "336 S;", "45 D;", "132 S;", "497 S;", "53 D;", "53 X;", "121 S;", "140 S;", "90 S;", "332 S;", "458 S;", "76 S;", "47 X;", "490 S;", "343 S;", "2 S;", "83 S;", "61 D;", "38 X;", "218 S;", "37 X;", "66 X;", "105 S;", "1 J;", "12 S;", "23 X;", "51 S;", "129 S;", "44 X;", "39 X;", "82 D;", "361 S;", "587 S;", "71 X;", "575 S;", "91 S;", "68 X;", "635 S;", "79 S;", "51 D;", "565 S;", "335 S;", "333 S;", "93 S;", "330 S;", "64 S;", "484 S;", "331 S;", "431 S;", "404 S;", "456 S;", "74 S;", "483 S;", "100 S;", "157 S;", "326 S;", "84 D;", "434 S;", "383 S;", "427 S;", "432 S;", "462 S;" ]
   rule_set["MISRA-C:2012"] = [ "48 S;", "506 S;", "252 S;", "12 X;", "33 X;", "87 S;", "74 D;", "61 S;", "567 S;", "26 X;", "62 X;", "429 S;", "31 X;", "480 S;", "20 S;", "87 D;", "610 S;", "81 S;", "72 D;", "621 S;", "5 X;", "63 X;", "271 S;", "248 S;", "36 D;", "54 S;", "11 S;", "120 S;", "35 S;", "98 D;", "553 S;", "63 D;", "496 S;", "25 X;", "52 S;", "18 D;", "613 S;", "270 S;", "1 S;", "95 S;", "441 S;", "637 S;", "15 X;", "580 S;", "69 S;", "21 S;", "616 S;", "19 X;", "126 S;", "65 S;", "442 S;", "550 S;", "493 S;", "57 S;", "69 D;", "243 S;", "344 S;", "27 X;", "430 S;", "123 S;", "42 D;", "384 S;", "293 S;", "128 S;", "338 S;", "7 C;", "127 S;", "412 S;", "20 X;", "89 D;", "341 S;", "611 S;", "10 X;", "477 S;", "70 X;", "9 X;", "62 D;", "9 S;", "487 S;", "1 D;", "486 S;", "451 S;", "92 S;", "437 S;", "7 X;", "73 S;", "30 S;", "47 S;", "444 S;", "337 S;", "112 S;", "62 S;", "135 S;", "428 S;", "104 S;", "632 S;", "48 D;", "389 S;", "122 S;", "130 S;", "48 X;", "14 X;", "1 Q;", "584 S;", "110 S;", "614 S;", "203 S;", "172 S;", "591 S;", "8 D;", "581 S;", "409 S;", "176 S;", "55 D;", "25 D;", "465 S;", "410 S;", "60 D;", "630 S;", "408 S;", "68 S;", "5 Q;", "482 S;", "16 X;", "406 S;", "36 X;", "61 X;", "64 X;", "636 S;", "60 S;", "145 S;", "28 D;", "96 S;", "1 X;", "494 S;", "2 D;", "103 S;", "71 S;", "612 S;", "426 S;", "323 S;", "75 S;", "590 S;", "113 S;", "606 S;", "13 S;", "631 S;", "495 S;", "156 S;", "345 S;", "436 S;", "296 S;", "125 S;", "342 S;", "374 S;", "329 S;", "4 X;", "147 S;", "134 S;", "86 S;", "219 S;", "76 D;", "489 S;", "29 X;", "78 S;", "407 S;", "439 S;", "17 S;", "39 S;", "50 D;", "36 S;", "49 S;", "106 D;", "461 S;", "3 J;", "34 D;", "249 S;", "11 X;", "302 S;", "385 S;", "50 X;", "438 S;", "325 S;", "30 X;", "403 S;", "450 S;", "520 S;", "576 S;", "620 S;", "80 S;", "324 S;", "72 S;", "446 S;", "435 S;", "1 U;", "94 S;", "149 S;", "6 X;", "49 D;", "17 X;", "59 S;", "77 D;", "511 S;", "63 S;", "276 S;", "53 S;", "32 X;", "509 S;", "589 S;", "131 S;", "44 S;", "136 S;", "245 S;", "72 X;", "67 X;", "6 D;", "22 X;", "66 S;", "91 D;", "22 D;", "43 D;", "445 S;", "50 S;", "582 S;", "554 S;", "107 S;", "114 S;", "43 S;", "28 X;", "622 S;", "413 S;", "119 S;", "26 D;", "83 D;", "69 X;", "8 X;", "21 X;", "24 X;", "18 X;", "27 D;", "37 S;", "101 S;", "626 S;", "545 S;", "382 S;", "143 S;", "15 D;", "488 S;", "397 S;", "57 X;", "17 D;", "33 D;", "340 S;", "573 S;", "443 S;", "433 S;", "35 X;", "452 S;", "88 S;", "322 S;", "35 D;", "13 X;", "102 S;", "615 S;", "139 S;", "481 S;", "110 D;", "440 S;", "34 X;", "623 S;", "336 S;", "105 D;", "45 D;", "132 S;", "497 S;", "627 S;", "53 D;", "53 X;", "121 S;", "140 S;", "90 S;", "332 S;", "458 S;", "104 D;", "76 S;", "47 X;", "343 S;", "83 S;", "61 D;", "38 X;", "218 S;", "37 X;", "113 D;", "66 X;", "105 S;", "1 J;", "629 S;", "65 D;", "12 S;", "23 X;", "51 S;", "39 X;", "82 D;", "361 S;", "14 D;", "628 S;", "587 S;", "75 D;", "71 X;", "575 S;", "68 X;", "635 S;", "51 D;", "565 S;", "531 S;", "335 S;", "333 S;", "411 S;", "93 S;", "330 S;", "64 S;", "484 S;", "331 S;", "431 S;", "404 S;", "74 S;", "483 S;", "100 S;", "217 S;", "118 S;", "157 S;", "326 S;", "608 S;", "103 D;", "84 D;", "434 S;", "383 S;", "427 S;", "432 S;" ]

   return(rule_set)