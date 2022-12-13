"""dialogue storage"""

greeting = [
    "[code]djep:o.[/code]",
    "[code]ax, ali.k ali.k raNi![/code]",
    "[code]tam jo di ali.k raNi, apr![/code]"
]
order = [
    "[code]aj, ja. a.laN [/code]{}[code], pi.vaN:ila[/code]",
    "[code]di raNi, ja. a.laN [/code]{}",
    "[code]o, ja a.laN di [/code]{}"
]
order_item = [
    "{count} [code]{itemname}[/code]"
] # use {translated} for translated item name
order_ok = [
    "[code]grama.t:a![/code]",
    "[code]aN:ka.ratl![/code]",
    "[code]sa.p:asi.ba![/code]",
    "[code]apr ali.k ali.k![/code]",
    "[code]a, Tut al:e ja. Pjetl, sa.p:asi.ba apr![/code]"
]
order_not_complete = [
    "[code]xm, jo a.laN ko al:e ja. fa'i![/code]",
    "[code]di Pjetl ko Tut![/code]",
    "[code]ja Pjetl ko. Tut apr[/code]"
]
order_too_many_items = [
    "[code]jo ka.plo a.frag a.frag[/code]",
    "[code]e.tr jom Pjetl i.la jo ka.plo?[/code]",
    "[code]ja. ko. fa'i xa. Pjetl[/code]",
    "[code]Ka.t:a fa'i xa. di? ko. ja.[/code]"
]
repeat_too_much = [
    "[code]e.tr jo a.laN j.a jom fa'i!?[/code]",
    "[code]ja. ko. aN:ka.ratl[/code]",
    "[code]jo fa.i fa.i ja., apr[/code]"
]
repeat_too_much_final = [
    "[code]ko. ja. fa'i, apr[/code]",
    "[code]di jasil, ko. al:e fa'i[/code]"
]
order_timeout = [
    "[code]ja. ko. a.laN raNi. xa. Pjetl![/code]",
    "[code]raNi jasil, apr[/code]"
]

translator_greeting = [
    "[color=teal]Conversation Detected[/color]\nInitiate traslation module",
]

translator_ordering = [
    "[color=teal]Ordering in progress[/color]\nTranslating order...",
]

translator_ok = [
    "[color=green]Transaction Sucessful[/color]\nWell done!",
]

translator_not_complete = [
    "[color=red]Transaction Failed[/color]\nPlease complete the order",
]

translator_too_many_items = [
    "[color=red]Transaction Failed[/color]\nToo many items",
]

translator_repeat_too_much = [
    "[color=yellow]!!WARNING!![/color]\nCease asking the customer to repeat their order",
]

translator_repeat_too_much_final = [
    "[color=red]Transaction Failed[/color]\nCustomer got annoyed",
]

translator_order_timeout = [
    "[color=red]Transaction Failed[/color]\nCustomer lost patience",
]
