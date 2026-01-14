from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Material, Stock, TruckIn, TruckOut, Quarry, Stock
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate



# --- Inventory Views ---


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pw')
        
       
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successful')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'signin.html')






def stock_add(request):
    materials = Material.objects.all()  # existing materials for dropdown

    if request.method == 'POST':
        material_id = request.POST.get('material')  # dropdown
        quantity = float(request.POST.get('qnty'))

        if not material_id:
            messages.error(request, "Please select a material")
            return redirect('stock_add')

        material = Material.objects.get(id=material_id)

        # ✅ Use get_or_create to avoid IntegrityError
        stock, created = Stock.objects.get_or_create(
            material=material,
            defaults={'quantity': quantity}
        )

        # If stock already exists, update the quantity
        if not created:
            stock.quantity += quantity
            stock.save()

        messages.success(request, f"Stock updated for {material.name}")
        return redirect('stock_list')

    return render(request, 'add_stock.html', {'materials': materials})





def edit_stock(request, id):
    stock = get_object_or_404(Stock, pk=id)
    materials = Material.objects.all()

    if request.method == 'POST':
        material_id = request.POST.get('material')
        quantity = request.POST.get('qnty')

        if not material_id or not quantity:
            messages.error(request, "All fields are required")
            return redirect('edit_stock', pk=id)

        material = get_object_or_404(Material, id=material_id)

        stock.material = material
        stock.quantity = float(quantity)
        stock.save()

        messages.success(request, "Stock updated successfully")
        return redirect('stock_list')

    return render(request, 'edit-stock.html', {
        'stock': stock,
        'materials': materials
    })
    
    
    
    
    
    
@transaction.atomic
def delete_stock(request, id):
    stock = get_object_or_404(Stock, pk=id)
    material = stock.material

    # 🔹 Rollback stock based on TruckIn and TruckOut entries
    # If you want to prevent deletion if any trucks exist:
    if TruckIn.objects.filter(material=material).exists() or TruckOut.objects.filter(material=material).exists():
        messages.error(request, "Cannot delete stock: There are existing truck entries for this material.")
        return redirect('stock_list')

    # Safe to delete
    stock.delete()
    messages.success(request, f"Stock for {material.name} deleted successfully.")
    return redirect('stock_list')





def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stock_list.html', {'stocks': stocks})



def truck_list(request):
    trucks = TruckIn.objects.all().order_by('-date')
    return render(request, 'truck_list.html',{'trucks':trucks})





def truck_out_list(request):
    trucks = TruckOut.objects.all().order_by('-date')
    return render(request, 'truck_out_list.html',{'trucks':trucks})




def material_add(request):
    if request.method =='POST':
        name = request.POST.get('name')
        
        materials = Material(name=name)
        materials.save()
        return redirect('stock_list')
    return render(request, 'add_material.html')



# --- Truck Views ---
def truck_in_add(request):
    materials = Material.objects.all()
    if request.method == 'POST':
        m = Material.objects.get(id=request.POST['material'])
        gross = float(request.POST['gross'])
        tare = float(request.POST['tare'])
        net = gross - tare
        TruckIn.objects.create(
            truck_number=request.POST['truck'],
            material=m,
            gross_weight=gross,
            tare_weight=tare,
            net_weight=net
        )
        stock, _ = Stock.objects.get_or_create(material=m)
        stock.quantity += net
        stock.save()
        return redirect('dashboard')
    return render(request, 'add_truck_in.html', {'materials': materials})





def truck_in_edit(request, pk):
    truck = get_object_or_404(TruckIn, pk=pk)
    materials = Material.objects.all()

    old_net = truck.net_weight
    old_material = truck.material

    if request.method == 'POST':
        material = get_object_or_404(Material, id=request.POST['material'])
        gross = float(request.POST['gross'])
        tare = float(request.POST['tare'])
        net = gross - tare

        # 🔹 Revert old stock
        old_stock, _ = Stock.objects.get_or_create(material=old_material)
        old_stock.quantity -= old_net
        old_stock.save()

        # 🔹 Update truck entry
        truck.truck_number = request.POST['truck']
        truck.material = material
        truck.gross_weight = gross
        truck.tare_weight = tare
        truck.net_weight = net
        truck.save()

        # 🔹 Add new stock
        stock, _ = Stock.objects.get_or_create(material=material)
        stock.quantity += net
        stock.save()

        messages.success(request, "Truck entry updated successfully")
        return redirect('truck_list')

    return render(request, 'edit_truck_in.html', {
        'truck': truck,
        'materials': materials
    })






def truck_in_delete(request, pk):
    truck = get_object_or_404(TruckIn, pk=pk)
    truck.delete()
    return redirect('truck_list')



def truck_out_add(request):
    materials = Material.objects.all()
    quarries = Quarry.objects.all()   # ✅ ADD THIS

    truck_numbers = (
        TruckIn.objects
        .values_list('truck_number', flat=True)
        .distinct()
        .order_by('truck_number')
    )

    if request.method == 'POST':
        m = Material.objects.get(id=request.POST['material'])
        gross = float(request.POST['gross'])
        tare = float(request.POST['tare'])
        net = gross - tare

        TruckOut.objects.create(
            truck_number=request.POST['truck'],
            material=m,
            gross_weight=gross,
            tare_weight=tare,
            net_weight=net,
            destination=request.POST['destination']
        )

        stock, _ = Stock.objects.get_or_create(material=m)
        stock.quantity -= net
        stock.save()

        return redirect('dashboard')

    return render(
        request,
        'add_truck_out.html',
        {
            'materials': materials,
            'truck_numbers': truck_numbers,
            'quarries': quarries,   # ✅ ADD THIS
        }
    )



def truck_out_edit(request, pk):
    truck = get_object_or_404(TruckOut, pk=pk)

    materials = Material.objects.all()
    quarries = Quarry.objects.all()

    truck_numbers = (
        TruckIn.objects
        .values_list('truck_number', flat=True)
        .distinct()
        .order_by('truck_number')
    )

    old_net = truck.net_weight
    old_material = truck.material

    if request.method == 'POST':
        material = get_object_or_404(Material, id=request.POST['material'])
        gross = float(request.POST['gross'])
        tare = float(request.POST['tare'])
        net = gross - tare

        # 🔹 ADD BACK old stock
        old_stock, _ = Stock.objects.get_or_create(material=old_material)
        old_stock.quantity += old_net
        old_stock.save()

        # 🔹 UPDATE TruckOut entry
        truck.truck_number = request.POST['truck']
        truck.material = material
        truck.gross_weight = gross
        truck.tare_weight = tare
        truck.net_weight = net
        truck.destination = request.POST['destination']
        truck.save()

        # 🔹 SUBTRACT new stock
        new_stock, _ = Stock.objects.get_or_create(material=material)
        new_stock.quantity -= net
        new_stock.save()

        messages.success(request, "Truck OUT updated successfully")
        return redirect('truck_out_list')

    return render(request,'edit-truck_out.html',
        {
            'truck': truck,
            'materials': materials,
            'truck_numbers': truck_numbers,
            'quarries': quarries,
        }
    )




@transaction.atomic
def truck_out_delete(request, pk):
    truck = get_object_or_404(TruckOut, pk=pk)

    # 🔹 Safely restore stock
    stock, _ = Stock.objects.get_or_create(material=truck.material)
    stock.quantity += truck.net_weight
    stock.save()

    # 🔹 Delete the TruckOut entry
    truck.delete()

    messages.success(request, f"Truck OUT entry deleted and stock restored.")
    return redirect('truck_out_list')




def quarry_add(request):
    if request.method =='POST':
        name = request.POST.get('quarry')
        location = request.POST.get('location')
        
        quarries = Quarry.objects.create(name=name, location=location)
        return redirect('quarry_list')
    return render(request, 'quarry_add.html')



def edit_quarry(request, id):
    quarry = Quarry.objects.get(pk=id)  

    if request.method == 'POST':
        quarry.name = request.POST.get('quarry')
        quarry.location = request.POST.get('location')
        quarry.save()
        return redirect('quarry_list')

    return render(request, 'edit_quarry.html', {
        'quarry': quarry
    })



def delete_quarry(request, id):
    quarry = get_object_or_404(Quarry, pk=id)
    quarry.delete()
    return redirect('quarry_list')




def quarry_list(request):
    quarries = Quarry.objects.all()
    return render(request, 'quarry_list.html',{'quarries':quarries})










def truck_history(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    export = request.GET.get('export')

    trucks_in = TruckIn.objects.all()
    trucks_out = TruckOut.objects.all()

    # Apply date filters
    if from_date and to_date:
        trucks_in = trucks_in.filter(date__range=[from_date, to_date])
        trucks_out = trucks_out.filter(date__range=[from_date, to_date])

    trucks_in = trucks_in.values(
        'date', 'time', 'truck_number', 'material__name', 'net_weight'
    )

    for t in trucks_in:
        t['type'] = 'IN'
        t['destination'] = '-'
        t['quantity'] = t['net_weight']

    trucks_out = trucks_out.values(
        'date', 'time', 'truck_number', 'material__name',
        'net_weight', 'destination'
    )

    for t in trucks_out:
        t['type'] = 'OUT'
        t['quantity'] = -t['net_weight']

    all_trucks = list(trucks_in) + list(trucks_out)
    all_trucks.sort(key=lambda x: (x['date'], x['time']), reverse=True)

    # ✅ EXPORT TO EXCEL
    if export == 'excel':
        return generate_excel(all_trucks, from_date, to_date)

    return render(request, 'truck_history.html', {
        'all_trucks': all_trucks,
        'from_date': from_date,
        'to_date': to_date
    })
    
    
    
    
    


def generate_excel(all_trucks, from_date, to_date):
    wb = Workbook()
    ws = wb.active
    ws.title = "Truck Movement Report"

    headers = [
        'Date', 'Time', 'Truck Number', 'Material',
        'Movement Type', 'Net Weight', 'Destination'
    ]
    ws.append(headers)

    for t in all_trucks:
        ws.append([
            t['date'],
            t['time'],
            t['truck_number'],
            t['material__name'],
            t['type'],
            t['net_weight'],
            t['destination']
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"truck_report_{from_date}_to_{to_date}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb.save(response)
    return response






def dashboard(request):
    today = now().date()
    daily_in = TruckIn.objects.filter(date=today).count()
    daily_out = TruckOut.objects.filter(date=today).count()
    total_in = TruckIn.objects.count()
    total_out = TruckOut.objects.count()
    return render(request, 'dashboard.html', {
        'daily_in': daily_in,
        'daily_out': daily_out,
        'total_in': total_in,
        'total_out': total_out
    })




def logout_view(request):
    logout(request)
    return redirect('login')