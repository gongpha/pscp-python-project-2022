"""dialogue storage"""

# (gongpha) : The uppercase strings are represented as the untranslated strings.
#               พิมพ์ใหญ่ คือ ข้อความที่ไม่ได้แปล เป็นภาษาไรไม่รู้
#             And Vice versa, the lowercase strings are represented as the translated strings.
#               พิมพ์เล็ก คือ ข้อความที่แปลแล้ว เป็นภาษาอังกฤษปกติ
#             Edit them as you want.
#               แก้ไขเองเบย

greeting = ["djep:o.", "ax, ali.k ali.k raNi!", "tam jo di ali.k raNi, apr!"]
order = ["aj, ja. a.laN {}, pi.vaN:ila", "di raNi, ja. a.laN {}", "o, ja a.laN di {}"]
order_item = ["{count} {itemname}"] # use {translated} for translated item name
order_ok = ["grama.t:a!", "aN:ka.ratl!", "sa.p:asi.ba!", "apr ali.k ali.k!", "a, Tut al:e ja. Pjetl, sa.p:asi.ba apr!"]
order_not_complete = ["xm, jo a.laN ko al:e ja. fa'i!", "di Pjetl ko Tut!", "ja Pjetl ko. Tut apr"]
order_too_many_items = ["jo ka.plo a.frag a.frag", "e.tr jom Pjetl i.la jo ka.plo?", "ja. ko. fa'i xa. Pjetl", "Ka.t:a fa'i xa. di? ko. ja."]
repeat_too_much = ["e.tr jo a.laN j.a jom fa'i!?", "ja. ko. aN:ka.ratl", "jo fa.i fa.i ja., apr"]
repeat_too_much_final = ["ko. ja. fa'i, apr", "di jasil, ko. al:e fa'i"]
order_timeout = ["ja. ko. a.laN raNi. xa. Pjetl!", "raNi jasil, apr"]