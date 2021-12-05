from django.shortcuts import render
from django.shortcuts import render, redirect
import cx_Oracle

# Create your views here.


def connect():
    dsn_tns = cx_Oracle.makedsn('128.196.27.219', '1521', service_name='ORCL') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    conn = cx_Oracle.connect(user=r'mis531group08', password='Ue/7eU1Wg', dsn=dsn_tns)
    cursor = conn.cursor()
    # cursor.execute('select * from donations')
    # result = cursor.fetchall()
    # for row in cursor:
    #     print(row[0])
    # print(result)
    # cursor.callproc('getuserstats',
    #                             ['2021'])
    
    # # cursor.execute('execute getuserstats("2021")')

    # cursor.callproc('addproducts',
    #                         ['Tada',5,'EMP8',50,'Purchase',40,5])

    # conn.commit()

    # out_val = cursor.var(int)
    # cursor.callproc('addproducts', ['Strawberri',5,'EMP8','50','Purchase',40,12])
    # print(out_val.getvalue())  


    # print(cursor.fetchall())
    # conn.close()

    return conn, cursor

def index(request):
    # connect()

    return render(request, "edmSubApp/index.html")

def login(request):
    return render(request, "edmSubApp/contact.html")

def loginauth(request):
    conn, cursor = connect()
    username = (request.POST['username']).strip()
    password = (request.POST['password']).strip()

    print(username,password)

    cursor.execute("select * from employee_login")

    result = cursor.fetchall()
    for e in result:
        if e[1] == username and e[2] == password:
            request.session['username'] = e[0]
            break
    else:
        print("Retry, Login Failed")
        return render(request, "edmSubApp/contact.html")

    conn.close()
    return render(request,"edmSubApp/index.html")

def addproducts(request):
    return render(request, "edmSubApp/addproducts.html")


def addproductsproc(request):
    conn, cursor = connect()
    employee_id = request.session.get('username')
    productname = (request.POST['productname']).strip()
    pointsperproduct = int((request.POST['pointsperproduct']).strip())
    priceperproduct = int((request.POST['priceperproduct']).strip())
    procurementtype = (request.POST['procurementtype']).strip()
    weight = int((request.POST['weight']).strip())
    quantity = int((request.POST['quantity']).strip())

    print(employee_id)


    cursor.callproc('addproducts',
                            [productname,pointsperproduct,employee_id,priceperproduct,procurementtype,weight,quantity])

    conn.commit()
    conn.close()
    return render(request,"edmSubApp/index.html")


def visitdetails(request):
    conn, cursor = connect()

    cursor.callproc('getuserstats',['2021'])
    cursor.execute('select * from useruservisitstatsview')

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request,"edmSubApp/visitdetails.html", context)

# q4 Monthly Products Per Visit
def monthlyproductspervisit(request):
    conn, cursor = connect()
    cursor.execute("""
        select l.locationname as "Location Name",
            avg(vd.quantity) as "Average Quantity"
        from visits v
            join visit_details vd on v.visitid = vd.visitid
            join locations l on l.locationid = v.locationid
        where l.locationname = 'Tucson'
            and v.visit_date between '01-MAY-21' and '31-MAY-21'
        group by l.locationname
        union
        select l.locationname as "Location Name",
            avg(vd.quantity) as "Average Quantity"
        from visits v
            join visit_details vd on v.visitid = vd.visitid
            join locations l on l.locationid = v.locationid
        where l.locationname = 'Eller'
            and v.visit_date between '01-MAY-21' and '31-MAY-21'
        group by l.locationname
        union
        select l.locationname as "Location Name", 
            avg(vd.quantity) as "Average Quantity"
        from visits v
            join visit_details vd on v.visitid = vd.visitid
            join locations l on l.locationid = v.locationid
        where l.locationname = 'Phoenix' 
            and v.visit_date between '01-MAY-21' and '31-MAY-21'
        group by l.locationname
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/monthlyproductspervisit.html", context)

# product statistics per visit q 10
def productstatistics(request):
    conn, cursor = connect()
    cursor.execute("""
        WITH t1 AS(
            SELECT DISTINCT
                prdr.productreceiptsid,
                prdr.totalweight
            FROM product_receipts prdR
            )
        SELECT 
            users.itemsweight AS "User Item Taken",
            t1.totalweight AS "Total Weight of Product", 
            ROUND((users.itemsweight/t1.totalweight) * 100,2) AS "Percent of Weight", 
            prd.productname AS "Product Name"
        FROM product_receipts_details prdrd
            JOIN t1 ON t1.productreceiptsid = prdrd.productreceiptsid
            JOIN products prd ON prd.productID = prdrd.productID
            JOIN products_taken_visits prdTV ON prd.productid = prdtv.productid
            JOIN product_receipts_details prdRD ON prd.productid = prdrd.productid
            JOIN VISITS Vis ON prdTV.visitID = Vis.visitID
            JOIN VISIT_DETAILS VisDet ON vis.visitid = visdet.visitid
            JOIN USERS ON users.catcardno = visdet.catcardno
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/productstatistics.html", context)


# q 16
def vistorsperlocationpermonth(request):
    conn, cursor = connect()
    cursor.execute("""
            WITH t1 AS (
            SELECT visitID AS "VisitID", 
            count(visitID) AS "Number of Visitors"
            FROM users
            JOIN visit_details visitD ON users.catcardno = visitd.catcardno
            GROUP BY visitd.visitid
            ), 
            t2 AS (
            SELECT loc.locationname, 
            loc.locationID
            FROM locations loc
            ), 
            t3 AS (
            SELECT COUNT (visitID) AS "number of people", 
            locationid AS "locationID"
            FROM visits
            GROUP BY locationid
            )
            SELECT 
            t2.locationname,
            t3.*,
            CASE
            when visits.visit_date LIKE '%%-JAN-%%' 
                or visits.visit_date LIKE '%%-01-%%' THEN 'JANUARY'
            when visits.visit_date LIKE '%%-FEB-%%' 
                or visits.visit_date LIKE '%%-02-%%' THEN 'FEBRUARY'
            when visits.visit_date LIKE '%%-MAR-%%' 
                or visits.visit_date LIKE '%%-03-%%' THEN 'MARCH'
            when visits.visit_date LIKE '%%-APR-%%' 
                or visits.visit_date LIKE '%%-04-%%' THEN 'APRIL'
            when visits.visit_date LIKE '%%-MAY-%%' 
                or visits.visit_date LIKE '%%-05-%%' THEN 'MAY'
            when visits.visit_date LIKE '%%-JUN-%%' 
                or visits.visit_date LIKE '%%-06-%%' THEN 'JUNE'
            when visits.visit_date LIKE '%%-JUL-%%' 
                or visits.visit_date LIKE '%%-07-%%' THEN 'JULY'
            when visits.visit_date LIKE '%%-AUG-%%' 
                or visits.visit_date LIKE '%%-08-%%' THEN 'AUGUST'
            when visits.visit_date LIKE '%%-SEP-%%' 
                or visits.visit_date LIKE '%%-09-%%' THEN 'SEPTEMBER'
            when visits.visit_date LIKE '%%-OCT-%%' 
                or visits.visit_date LIKE '%%-10-%%' THEN 'OCTOBER'
            when visits.visit_date LIKE '%%-NOV-%%' 
                or visits.visit_date LIKE '%%-11-%%' THEN 'NOVEMBER'
            when visits.visit_date LIKE '%%-DEC-%%' 
                or visits.visit_date LIKE '%%-12-%%' THEN 'DECEMBER'
            end AS "Month of Visit"
            FROM t1 
            JOIN visits ON visits.visitid = t1."VisitID"
            JOIN t2 ON t2.locationID = visits.locationid
            JOIN t3 ON t3."locationID" = visits.locationid
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/vistorsperlocationpermonth.html", context)


def moneyprocured(request):
    conn, cursor = connect()
    cursor.execute("""
        with a1 as (
            select dd.DONORID as "Donor ID", 
            dd.donorname as "Donor Name",
            dd.DONORTYPE as "Donor Type", 
            d.DONATIONAMOUNT as "Donation Amount", 
            RANK() OVER (ORDER BY DONATIONAMOUNT DESC) as "Rank" 
        FROM donors DD 
            JOIN DONATIONS D ON DD.DONORID = D.DONORID
        ), 
        a2 AS (
        select DD.DONORID as "Donor ID",  
            F.FINDATE as "Financial Date" 
        FROM DONATIONS DD 
            JOIN FINANCIALS F ON DD.FINANCIALID = F.FINANCIALID
        )
        select a1."Donor ID", a1."Donor Name", a1."Donor Type", 
            a2."Financial Date" as "Date of Donation",  
            to_char(a1."Donation Amount", '$999,999') as "Donation Amount", a1."Rank"
        from a1
        JOIN a2 ON a1."Donor ID" = a2."Donor ID"
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/moneyprocured.html", context)

def fundsbytype(request):
    conn, cursor = connect()
    cursor.execute("""
        with a1 as (
            select
                f.fundraisingtype as "Fundraising Type",
                sum(amountOfMoneyPledged) as "Total"
            from PLEDGES p
                    join fundraising f on f.fundraisingid = p.fundraisingid
            group by f.fundraisingtype
            union
            select
                f.fundraisingtype as "Fundraising Type",
                sum(weight*1.70) as "Total"
            from FOOD_DRIVES fd
                    join fundraising f on f.fundraisingid = fd.fundraisingid
            group by f.fundraisingtype
        )
        select "Fundraising Type", to_char(a1."Total", '$999') as "Total"
        from a1
        order by "Total" desc
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/fundsbytype.html", context)

def workshistory(request):
    conn, cursor = connect()
    cursor.execute("""
        select se.empid as "ID",
            case
                when se.empid like 'EMP%' then 'Employee'
                end as "Type"
            ,se.first_name || ' ' || se.last_name as "Name", 
            sum(wh.hoursworked)as "Total Hours Worked",
            avg(wh.hoursworked) as "Average Hours Worked"
        from student_works_history swh
            join work_history wh on wh.workhistoryid = swh.workhistoryid
            join student_employees se on swh.empid = se.empid
        group by se.empid, se.first_name || ' ' || se.last_name
        union
        select v.volunteerid as "ID",
            case
                when v.volunteerid like 'VOL%' then 'Volunteer'
                end as "Type"
            ,v.first_name || ' ' || v.last_name as "Name", 
            sum(vs.hours_worked) as "Total Hours Worked", 
            avg(vs.hours_worked) as "Average Hours Worked"
        from volunteer_sessions vs
            join volunteers v on vs.volunteerid = v.volunteerid
        group by v.volunteerid, v.first_name || ' ' || v.last_name
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/workshistory.html", context)


def grantlevels(request):
    conn, cursor = connect()
    cursor.execute("""
        with a1 as (
        select  
            grantid,
            grantamount,
            case
            when grantamount < 2000 then 'Low'
            when grantamount > 3000 and grantamount < 5000 then 'Medium'
            when grantamount > 5000 and grantamount < 10000 then 'High'
            end as  "Grant Level" 
        from grants
        )
        select 
            "Grant Level",
            count(grantid) as "Number of Grants",
            to_char(sum(grantamount), '$99,999') as "Total Amount"
        from a1
        group by "Grant Level"
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/grantlevels.html", context)

def employeeproductcheckins(request):
    conn, cursor = connect()
    cursor.execute("""
            with a1 as (
            Select p.empID as "Employee ID", count( (p.empid)) AS "Products Entered"
            From products p
            Group by p.empID
            ),
            a2 as (
            select se.empID,
            SE.FIRST_NAME || ' ' || SE.LAST_NAME "Employee Name" 
            from student_employees SE
            ),
            a3 as (
            select
            a1."Employee ID",
            RANK() over (ORDER BY a1."Products Entered" DESC) AS "Rank" from a1
            )
            select a1."Employee ID", a2."Employee Name", a1."Products Entered",  a3."Rank"
            from a1 join a2 on a1."Employee ID" = a2.empid 
            join a3 on a1."Employee ID"= a3."Employee ID"
            order by a3."Rank"
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/employeeproductcheckins.html", context)

def volunteersessions(request):
    conn, cursor = connect()
    cursor.execute("""
            WITH t1 AS (
            SELECT
            sessionID AS "Session ID", 
            count(sessionID) AS "Number of Volunteers"
            FROM volunteer_sessions
            GROUP BY sessionID)

            SELECT 
            t1.*,
            volunteer_sessions.date_worked as "Date Worked"
            FROM volunteer_sessions
            JOIN t1 ON volunteer_sessions.sessionid = t1."Session ID"
            ORDER BY t1."Number of Volunteers" ASC
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/volunteersessions.html", context)


def volunteersperlocation(request):
    conn, cursor = connect()
    cursor.execute("""
        with a1 as (
        SELECT 
            extract(month from volsess.date_worked) month,
            loc.locationname AS "Location Name",
            COUNT(vol.volunteerid) AS "Number of Volunteers", SUM (volsess.hours_worked) as "Total Volunteer Hours"
        FROM volunteer_sessions volSess
            JOIN volunteers Vol ON vol.volunteerid = volsess.volunteerid
            JOIN locations loc ON  volsess.locationid = loc.locationid
        WHERE date_worked >= '01-AUG-21'
        GROUP BY loc.locationname, extract(month from volsess.date_worked)
        ),
        a2 as (
        select
        case
        when month=1 then 'Janurary'
        when month=2 then 'Feburary'
        when month=3 then 'March'
        when month=4 then 'April'
        when month=5 then 'May'
        when month=6 then 'June'
        when month=7 then 'July'
        when month=8 then 'August'
        when month=9 then 'September'
        when month=10 then 'October'
        when month=11 then 'November'
        when month=12 then 'December'
        end as Month, "Location Name",
        "Number of Volunteers",
        "Total Volunteer Hours"
        from a1)
        select * from a2
    """)

    result = cursor.fetchall()
    print(result)

    conn.close()
    context = {"visitdetails" : result}
    return render(request, "edmSubApp/volunteersperlocation.html", context)
