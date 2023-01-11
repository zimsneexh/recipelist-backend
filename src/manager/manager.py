class manager():

    recipe_list = [ ]

    def add_recipe_list(self, art):
        manager.recipe_list= art
    

    def get_article_by_id(self, target_id):
        for a in manager.recipe_list:
            if(a.id == target_id):
                return a

        return None
