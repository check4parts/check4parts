import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:staff');
	const { data: staff } = await supabase
		.from('staff')
		.select('*,roles(name),trading_points(*)')
		.order('first_name');
	return { staff: staff ?? [] };
};
