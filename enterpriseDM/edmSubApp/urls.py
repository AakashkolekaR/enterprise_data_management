from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path("",views.index, name = "index"),
    path("login", views.login, name = "login"),
    path("loginauth", views.loginauth, name="loginauth"),
    path("logout", views.logout, name="logout"),
    path("productlisting", views.productlisting, name = "productlisting"),
    path("addproducts", views.addproducts, name="addproducts"),
    path("addproductsproc", views.addproductsproc, name="addproductsproc"),
    path("visitdetails", views.visitdetails, name="visitdetails"),
    path("monthlyproductspervisit", views.monthlyproductspervisit, name="monthlyproductspervisit"),
    path("productstatistics", views.productstatistics, name="productstatistics"),
    path("vistorsperlocationpermonth", views.vistorsperlocationpermonth, name="vistorsperlocationpermonth"),
    path("moneyprocured", views.moneyprocured, name="moneyprocured"),
    path("fundsbytype", views.fundsbytype, name="fundsbytype"),
    path("workshistory", views.workshistory, name="workshistory"),
    path("grantlevels", views.grantlevels, name="grantlevels"),
    path("employeeproductcheckins", views.employeeproductcheckins, name="employeeproductcheckins"),
    path("volunteersessions", views.volunteersessions, name="volunteersessions"),
    path("volunteersperlocation", views.volunteersperlocation, name="volunteersperlocation"),
    path("productreceipts", views.productreceipts, name="productreceipts"),
    path("employeeinfo", views.employeeinfo, name="employeeinfo"),
    path("visitdetailsquery", views.visitdetailsquery, name="visitdetailsquery"),

]
