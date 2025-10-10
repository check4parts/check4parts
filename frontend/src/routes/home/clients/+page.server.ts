import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
    depends('supabase:db:clients');
    const { data: clients } = await supabase
        .from('clients')
        .select('*')
        .order('first_name');
    return { clients: clients ?? [] };
};
