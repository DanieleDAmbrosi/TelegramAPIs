record = ("Ciao", 1, 2, 3, "NULL")
record1 = ("Ciao", 1, 2, 3, "", "NULL")
record2 = ("Ciao", 1, 2, 3, "IsOk")



for rec in [record, record2, record1]:
    if all([len(x.strip()) != 0 and x != "NULL" for x in map(str, rec)]):
        print(rec)