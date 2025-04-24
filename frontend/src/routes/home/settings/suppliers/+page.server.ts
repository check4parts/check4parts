import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:company_provider');
	const { data: suppliers } = await supabase.from('company_provider').select('*,providers(*)');

	return { suppliers: suppliers ?? [] };
};
