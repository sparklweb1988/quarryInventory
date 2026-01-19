from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Material, Stock, TruckIn, TruckOut, Quarry, Stock,Project, Task, Company
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import ProjectForm, TaskForm





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






from django.shortcuts import render
from django.utils.timezone import now
from .models import Project, Task, TruckIn, TruckOut

def dashboard(request):
    # 1️⃣ Get the company for the logged-in user
    # Adjust this depending on your User model
    # Example: user has a related company
    company = request.user.company  

    # 2️⃣ Query projects and tasks for this company
    projects = Project.objects.filter(company=company)
    tasks = Task.objects.filter(company=company)

    # 3️⃣ Truck statistics
    today = now().date()
    daily_in = TruckIn.objects.filter(date=today).count()
    daily_out = TruckOut.objects.filter(date=today).count()
    total_in = TruckIn.objects.count()
    total_out = TruckOut.objects.count()

    # 4️⃣ Pass context to template
    context = {
        'daily_in': daily_in,
        'daily_out': daily_out,
        'total_in': total_in,
        'total_out': total_out,
        'projects': projects,
        'tasks': tasks,
        'total_projects': projects.count(),
        'completed_projects': projects.filter(status='completed').count(),
        'pending_tasks': tasks.exclude(status='done').count(),
        'project_status_counts': {
            'Planned': projects.filter(status='planned').count(),
            'Ongoing': projects.filter(status='ongoing').count(),
            'Completed': projects.filter(status='completed').count(),
        },
        'task_status_counts': {
            'To Do': tasks.filter(status='todo').count(),
            'In Progress': tasks.filter(status='progress').count(),
            'Done': tasks.filter(status='done').count(),
        },
    }

    return render(request, 'dashboard.html', context)




def project_list(request):
    company = get_current_company(request)
    projects = Project.objects.filter(company=company)
    return render(request, 'project_list.html', {'projects': projects})




def get_current_company(request):
    # Logged-in user
    if request.user.is_authenticated:
        company, _ = Company.objects.get_or_create(
            owner=request.user,
            defaults={'name': f"{request.user.username}'s Company"}
        )
        return company

    # Anonymous user (session-based)
    company_id = request.session.get('company_id')

    if company_id:
        return Company.objects.get(id=company_id)

    company = Company.objects.create(name='Guest Company')
    request.session['company_id'] = company.id
    return company





def project_add(request):
    company = get_current_company(request)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.company = company
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'project_form.html', {'form': form, 'title': 'Add Project'})






def project_edit(request, pk):
    company = get_current_company(request)
    project = get_object_or_404(Project, pk=pk, company=company)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_form.html', {'form': form, 'title': 'Edit Project'})



def project_delete(request, pk):
    company = get_current_company(request)
    project = get_object_or_404(Project, pk=pk, company=company)
    project.delete()
    return redirect('project_list')



def project_mark_complete(request, pk):
    company = get_current_company(request)
    project = get_object_or_404(Project, pk=pk, company=company)
    project.status = 'completed'
    project.save()
    return redirect('project_list')





def task_list(request):
    company = get_current_company(request)
    tasks = Task.objects.filter(company=company)
    return render(request, 'task_list.html', {'tasks': tasks})



def task_add(request):
    company = get_current_company(request)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.company = company
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {'form': form, 'title': 'Add Task'})





def task_edit(request, pk):
    company = get_current_company(request)
    task = get_object_or_404(Task, pk=pk, company=company)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {'form': form, 'title': 'Edit Task'})



def task_delete(request, pk):
    company = get_current_company(request)
    task = get_object_or_404(Task, pk=pk, company=company)
    task.delete()
    return redirect('task_list')



def task_mark_complete(request, pk):
    company = get_current_company(request)
    task = get_object_or_404(Task, pk=pk, company=company)
    task.status = 'done'
    task.save()
    return redirect('task_list')
















def logout_view(request):
    logout(request)
    return redirect('login')