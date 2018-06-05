from flask import request, Blueprint, render_template, redirect, url_for, flash
from my_app.source.models import cursor, conn
my_app = Blueprint('app', __name__)
from my_app.source.models import ReviewForm
# from flask_bootstrap import Bootstrap


#-------------------- Home Page Handler --------------------

@my_app.route('/')
def base():
    return render_template("homepage.html")

@my_app.route('/home')
def homePage():
    return render_template("homepage.html")

#-------------------- Organization Handler --------------------

@my_app.route('/organizations')

def organizations():
    command = """SELECT {a}.organization_id, {a}.organization_name, {a}.president, {a}.number_of_members, {b}.category_name, {a}.rating
                 FROM {a} join {b} ON {a}.category_id = {b}.category_id
        """.format(a="organization", b='category')
    cursor.execute(command)
    org_data = cursor.fetchall()

    return render_template("organization.html",org_list=org_data)

#-------------------- Further Details Handler --------------------

# @my_app.route('/details')
#
# def details():
#     command = """SELECT {c}.club_id, {a}.organization_name, {c}.location, {c}.number_of_reviews, {c}.payment_required, {c}.membership_cost
#                           FROM {c} join {a} ON {c}.club_id = {a}.club_id
#             """.format(a="organizations", c='details')
#     cursor.execute(command)
#     club_data2 = cursor.fetchall()
#
#
#     return render_template("sub_table.html", sub_list = club_data2)

#-------------------- Organization Detail Handler --------------------

#Parameters: Key, integer
@my_app.route('/organizations/organization_detail/<key>') #Ways to control the parameter

def get_message(key):

    command = """ SELECT {a}.organization_name, {a}.organization_id, {a}.description, {a}.location, {a}.president,
                         {a}.membership_cost, {a}.is_payment_required, {a}.rating, {a}.number_of_members, {a}.Image_URL
                         FROM {a}
                         WHERE {a}.organization_id = {p1}
    """.format(a="organization", p1=key)

    cursor.execute(command)
    club_data3 = cursor.fetchall()
    if len(club_data3) == 0:
        return "Page Error. The key " + key + " cannot be found"
    individual_club = club_data3[0]

    return render_template("organization_detail.html",org_detail = individual_club)



# --------------- Category Handler ------------------#

@my_app.route('/category')
def show_categories():
    command = """SELECT {b}.category_id, {b}.category
                FROM {b}
                """.format(b='category')

    cursor.execute(command)
    club_data = cursor.fetchall()

    return render_template("category.html", club_category = club_data)


#------------------ Individual Category Pages Handler ----------------

@my_app.route('/category/<key>')

def one_category(key):

    command = """SELECT {a}.club_id, {a}.organization_name, {a}.president, {a}.number_of_members, {b}.category, {a}.rating
                      FROM {a} join {b} ON {a}.category_id = {b}.category_id
                      WHERE {b}.category_id = {k}
        """.format(a="organizations", b='category', k=key)

    cursor.execute(command)
    club_data = cursor.fetchall()

    return render_template("organization.html", club_list = club_data)




#------------------ Organization Search ----------------
@my_app.route('/organization_search', methods = ["GET","POST"])

def organization_search():

    org_name = request.args.get('org_name')
    condition = ""

    if org_name != None:
        condition += "organization.organization_name LIKE '%"+(org_name)+"%'"

    if condition == "":
        command = """SELECT {a}.organization_id, {a}.organization_name, {a}.president, {a}.number_of_members, {b}.category_name, {a}.rating
                     FROM {a} join {b} ON {a}.category_id = {b}.category_id
                  """.format(a="organization", b='category')
    else:
        command = """SELECT {a}.organization_id, {a}.organization_name, {a}.president, {a}.number_of_members, {b}.category_name, {a}.rating
                      FROM {a} join {b} ON {a}.category_id = {b}.category_id
                      WHERE {cond}
        """.format(a="organization", b='category', cond=condition)

    cursor.execute(command)
    org_data = cursor.fetchall()
    return render_template("organization.html", org_list = org_data)

#--------------------Review Page Handler---------------

#Parameters: Key
@my_app.route ('/reviews/<key>', methods = ['GET','POST'])

def insert_review(key):
    # This queries the review list. This should be put on the individual pages.
    command = """SELECT {a}.review_id, {a}.first_name, {a}.last_name,{a}.organization_name, {a}.user_review
                              FROM {a}
                      """.format(a='review')
    cursor.execute(command)
    review_data = cursor.fetchall()


    # This queries the review_id and make it autoincrement
    command = """ SELECT MAX(review_id)
                    FROM review
            """
    cursor.execute(command)
    next_id = cursor.fetchone()
    if next_id[0] == None:
        review_id = 1
    else:
        review_id = next_id[0]+1
# -------------------------------------------

    # How do we select the associated organization_id
    command = """ SELECT {a}.organization_id
                  FROM {a}
                  WHERE {a}.organization_id = {id}
    """.format(a='organization', id = key )
    cursor.execute(command)
    selected_org_id = cursor.fetchone()

#----------------------------------------------------------
    form = ReviewForm(request.form, crsf_enabled=False)# This variable is linked to models.py

    command = """ SELECT organization_name, organization_name
                       FROM organization
               """
    cursor.execute(command)
    org_name = cursor.fetchall()
    form.org_name.choices = org_name

    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data # This variable is linked to the models
        org_name = form.org_name.data
        user_review = form.user_review.data
        org_id = selected_org_id[0]


        # This command only works when if request.method == POST
        command = """ INSERT INTO review (review_id, first_name, last_name, organization_name, user_review, organization_id)
                      VALUES ({i},'{f}','{l}','{n}','{r}',{o})
                  """.format(i=review_id, f=first_name, l=last_name, n=org_name, r=user_review, o=org_id) #This format matches the models and if POST statement
        cursor.execute(command)
        conn.commit()
        # flash is a pop up?
        flash('Your Review has been added','success')
        # return redirect(url_for('app.insert_review'))

    if form.errors:
        flash(form.errors, 'danger')
          # This request's syntax is the router.(html file)
        # The user will be directed to this URL. The database should already be inserted and able to be viewed once redirected

    return render_template('reviewpage.html', form=form, review_list=review_data)


#---------------- Individual Edit Key Handler --------------#
@my_app.route('/edit/<key>')
def edit(key):
    command = """SELECT {a}.id, {a}.first_name, {a}.last_name, {a}.organization_name, {a}.user_review
                      FROM {a}
                      WHERE {a}.id = {p1}
        """.format(a="reviews", p1=key)
    cursor.execute(command)
    edit_data = cursor.fetchall()

    if len(edit_data) == 0:
        return "The key " + key + " was not found"
    edit = edit_data[0]

    return render_template('edit.html', one_edit=edit)


#---------------- Edit Review Handler----------------#
@my_app.route('/review_edit/<key>', methods = ['GET','POST'])
def review_edit(key):
    command = """ SELECT *
                    FROM reviews
                    WHERE id = {p1}
            """.format(p1=key)
    cursor.execute(command)
    single_review = cursor.fetchall()[0]

    form = ReviewForm(request.form, csrf_enabled=False, first_name=single_review[1], last_name=single_review[2],
                       organization_name=single_review[3], user_review=single_review[4])

    command = """ SELECT Organization_name, Organization_name
                           FROM Organizations
                   """
    cursor.execute(command)
    club_name = cursor.fetchall()

    form.org_name.choices = club_name

    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data # This variable is linked to the models
        org_name = form.org_name.data
        user_review = form.user_review.data # This command only works when if request.method == POST

        command = """
            UPDATE reviews SET first_name='{f}', last_name='{l}',organization_name='{o}',user_review='{u}'
            WHERE id ={i}
            """.format(f=first_name, l=last_name, o=org_name, u=user_review, i=key)
        cursor.execute(command)
        conn.commit()

        flash('Your Review has been edited', 'success')
        return redirect(url_for('app.insert_review'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('review-edit.html',form=form, review_id=key)



#----------------- Delete Review Handler-------------#
@my_app.route('/reviews/delete/<key>', methods = ['GET','POST'])
def review_delete(key):
    command = """ SELECT *
                    FROM reviews
                    WHERE id = {p1}
            """.format(p1=key)
    cursor.execute(command)

    command = """ DELETE FROM reviews
                    WHERE id = {p1}
            """.format(p1=key)
    cursor.execute(command)
    conn.commit()

    flash('Your Review has been deleted')
    return redirect(url_for('app.insert_review', index = key))

#-------------Search Handler----------------------#
# @my_app.route("/search", methods = ['GET','POST'])
#
# def search_organization():
