import { fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
    depends('supabase:db:clients');
    depends('supabase:db:client_types');
    const [clientsResponse, clientTypesResponse] = await Promise.all([
        supabase.from('clients').select('*,cars(*)'),
        supabase.from('client_types').select('*'),
    ]);

    if (clientsResponse.error) {
        console.error('Error fetching providers:', clientsResponse.error);
        throw fail(500, { message: 'Failed to load providers.' });
    }

    if (clientTypesResponse.error) {
        console.error('Error fetching warehouses:', clientTypesResponse.error);
        throw fail(500, { message: 'Failed to load warehouses.' });
    }


    return { clients: clientsResponse.data ?? [], clientTypes: clientTypesResponse.data ?? [] };
};