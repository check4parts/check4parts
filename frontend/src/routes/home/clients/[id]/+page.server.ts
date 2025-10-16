import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ depends, locals: { supabase }, params }) => {
    depends('supabase:db:clients');
    depends('supabase:db:client_types');
    const client_id = params.id;
    const { data: client } = await supabase
        .from('clients')
        .select('*,cars(*),client_types(*)')
        .eq('id', client_id)
        .single();

    const { data: client_types } = await supabase
        .from('client_types')
        .select('*')
        .order('name', { ascending: true });

    return { client: client ?? {}, types: client_types ?? [] };
};

export const actions = {
    edit: async ({ request, locals: { supabase }, params }) => {
        const client_id = params.id;
        const formData = await request.formData();

        const first_name = formData.get('first_name')?.toString();
        const last_name = formData.get('last_name')?.toString();
        const middle_name = formData.get('middle_name')?.toString();
        const phone_number = formData.get('phone')?.toString();
        const address = formData.get('address')?.toString();
        const note = formData.get('note')?.toString();
        const type_id = formData.get('type_id')?.toString();

        const { error } = await supabase
            .from('clients')
            .update({
                first_name,
                last_name,
                middle_name,
                phone_number,
                address,
                note,
                type_id: type_id === '' ? null : type_id
            })
            .eq('id', client_id);

        if (error) {
            return { success: false, message: error.message };
        }

        return { success: true, message: 'Клієнта успішно оновлено' };
    },
    delete: async ({ locals: { supabase }, params }) => {
        const client_id = params.id;

        const { error } = await supabase.from('clients').delete().eq('id', client_id);

        if (error) {
            return { success: false, message: error.message };
        }

        return { success: true, message: 'Клієнта успішно видалено' };
    },
    addCar: async ({ request, locals: { supabase }, params }) => {
        const client_id = params.id;
        const formData = await request.formData();

        const name = formData.get('name')?.toString();
        const vin_code = formData.get('vin')?.toString();
        const license_plate = formData.get('license_plate')?.toString();

        const { error } = await supabase.from('cars').insert({
            client_id,
            name,
            vin_code,
            license_plate
        });

        if (error) {
            console.error('Error adding car:', error);
            return { success: false, message: error.message };
        }

        return { success: true, message: 'Автомобіль успішно додано' };
    },
    editCar: async ({ request, locals: { supabase } }) => {
        const formData = await request.formData();

        const id = formData.get('id')?.toString();;
        const name = formData.get('name')?.toString();
        const vin_code = formData.get('vin')?.toString();
        const license_plate = formData.get('license_plate')?.toString();

        const { error } = await supabase.from('cars').update({
            name,
            vin_code,
            license_plate
        }).eq('id', id);

        if (error) {
            console.error('Error editing car:', error);
            return { success: false, message: error.message };
        }

        return { success: true, message: 'Автомобіль успішно оновлено' };

    },
    deleteCar: async ({ request, locals: { supabase } }) => {
        const formData = await request.formData();
        const id = formData.get('id')?.toString();;

        const { error } = await supabase.from('cars').delete().eq('id', id);

        if (error) {
            console.error('Error deleting car:', error);
            return { success: false, message: error.message };
        }

        return { success: true, message: 'Автомобіль успішно видалено' };
    }
}
