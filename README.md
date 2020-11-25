Jméno a příjmení: David Rubý\

>## interpret.py
>Dvou průchodový interpret XML reprezentace jazyka IPPcode20
>1. Interpret rozparsuje veškeré argumenty zadané při spuštění scriptu a otestuje jejich případné konflikty. Dále si uloží potřebné hodnoty do proměnných a nastaví vstupní a výstupní zdroje
>1. Ze vstupního zdroje zadaného v argumentech si přečte XML reprezentaci jazyka IPPcode20 a pomocí knihovny ``xml.etree.ElementTree`` jej převede do interní reprezentace XML struktury.
>1. projde veškeré elementy ``instruction`` od začátku do konce a když má instrukce daná intrukce ``opcode`` atribut hodnotu ``LABEL``, uloží si jeji pozici v programu do slovníku návěští.
>2. V druhém průchodu strukturou ignoruje ``LABEL`` atributy a veškré ostatní provádí. Každá instrukce má vlastní funkci, ve které se kontroluje a následně vykonává
> ### interní proměnné:
>>#### ``pc``:
>> Uchovavá aktuální pozici v průchodu XML strukturou. Může se modifikovat například při provádění instrukce ``JUMP``, ``JUMPIFEQ``, ``JUMPIFNEQ`` a podobně.
>
>>#### ``pc_stack``:
>> Zásobník hodnot, uchovávající pozice v průchodu XML strukturou. Při provádění instrukce ``CALL`` se uloží aktuální pozice na zásobník. Při provádění instrukce ``RETURN`` se tato hodnota výjme z tohoto zásobníku a průchod XML strukturou pokračuje od této pozice.
>
>>#### ``instruction_counter``:
>> Uchovává celkový počet již provedených instrukcí.
>
>>#### ``gf_counter``, ``lf_counter`` a ``tf_counter``:
>> Uchovávají celkový počet uložených proměnných v těchto rámcích.
>
>>#### ``data_stack``:
>>Zásobník hodnot. Při provádění instrukce ``PUSHS`` se uloží se na tento zásobník uloží hodnota a aři provádění instrukce ``POPS`` se výjme hodnota z vrcholu tohoto zásobníku. Tento zásobník se hojně využívá u rozšiření, které přidává zásobníkové verze některý instrukcí.
>
>>#### ``gf``, ``lf`` a ``tf``:
>> Jedná se slovníky, kde se na pozici klíče vyskytuje jméno proměnné a v hodnotě její hodnota. ``lf`` je pole takovýchto  slovníků.
