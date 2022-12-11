"""dialogue storage"""

# (gongpha) : The uppercase strings are represented as the untranslated strings.
#               พิมพ์ใหญ่ คือ ข้อความที่ไม่ได้แปล เป็นภาษาไรไม่รู้
#             And Vice versa, the lowercase strings are represented as the translated strings.
#               พิมพ์เล็ก คือ ข้อความที่แปลแล้ว เป็นภาษาอังกฤษปกติ
#             Edit them as you want.
#               แก้ไขเองเบย

greeting = "HOWDY"
order = "CAN I HAVE {}, PLEASE?"
order_item = "{count}x [code]{itemname}[/code]" # use {translated} for translated item name
order_ok = "THANKS!"
order_not_complete = "THE ORDER IS NOT COMPLETE!"
order_too_many_items = "PERHAPS YOU SHOULD CLEAN YOUR COUNTER."
repeat_too_much = "WHY ARE YOU KEEPING ME REPEATING?"
repeat_too_much_final = "STOP KEEPING ME REPEATING! I'M TIRED!"
order_timeout = "I DON'T HAVE TIME FOR THIS!"