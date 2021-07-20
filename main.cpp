// This code is property of the fat body prince
/*
	Name: Maram "Mara" Sreerama Reddy
	Reg : 206120017
	MTech 2020-22 - NIT Tiruchirappalli
*/

#include <bits/stdc++.h>
using namespace std;

class CEFT{
	int V, np;
	// Variables to store the results
	vector<vector<pair<int, int>>>aval_time;
	list<pair<int, int>> *adj, *adj_original; // Copy to original grapgh because we will delete nodes during
	vector<vector<int>> FinalSchedule, exec_time, qs;      // finding critical paths phase
	vector<list<int>>CP;
	vector<unordered_set<int>>dpends;
	vector<bool>done;
	vector<int>prec, predes;

	public:
		CEFT(){ 							// Contructor to take input data
			/*
				Input Data includes:
					Graph -> nodes, edges, weights
					Processors -> performance index, execution time against each process
			*/

			// Processors Data
			int p, ind = 0; cin >> p;
			this->np = p;
			aval_time.resize(p);

			// Graph Data, resizing data structures according to no. if nodes and edges
			int n, e, u, v, w; ind = 0;
			cin >> n >> e;
			this->V 		= 	n;
			adj 			= 	new list<pair<int, int>>[V];
			adj_original 	= 	new list<pair<int, int>>[V];
			exec_time.resize(this->np, vector<int>(this->V));
			prec.resize(n, -1); done.resize(n, false);
			dpends.resize(n); predes.resize(n, -1);
			for(int i = 0; i < this->np; i++)
				for(int j = 0; j < this->V; j++)
					cin >> exec_time[i][j];

			// Input of graph edges, weights
			while(e--){
				cin >> u >> v >> w;
				this->add_edge(u, v, w);
			}
		}

		void add_edge(int n1, int n2, int w){
			// Adding edge n1->n2 to the graph with weight w.
			if(n1 >= V || n2 >= V){
				printf("ERROR DA! You say there are %d no. of vertices and give vertex number as %d. What is this da! Only 0-%d are allowed.\n EXITING!! START AGAIN!!\n\n", V, max(n1, n2), V-1);
				exit(0);
			}
			adj_original[n1].push_back({n2, w});
			adj[n1].push_back({n2, w});
		}

		void delete_nodes(vector<bool>included){
			// deleting the nodes and incident edges from graph (included has boolean true for nodes to be removed)
			for(int v = 0; v < V; v++){
				if(included[v]){
					adj[v].clear(); continue;
				}
				for(list<pair<int, int>>::iterator el=adj[v].begin(); el!=adj[v].end(); el++){
					int w = (*el).first;
					if(included[w]) adj[v].erase(el);
				}
			}
		}

		void add_pseudo_nodes(){
			// Adding Pseudo edges to nodes who have no Predesessor ot Successor
			vector<int>in_degree(V, 0);
			vector<int>out_degree(V, 0);
			for(int v = 0; v < V; v++){
				if(v!=0 && v!=V-1)
					out_degree[v] = adj[v].size();
				for(auto x: adj[v]){
					int w = x.first;
					if(w==0 || w==V-1) continue;
					in_degree[w]++;
				}
			}

			for(int v = 1; v < V-1; v++){
				if(done[v]) continue;
				if(in_degree[v] == 0)
					adj[0].push_back({v, 0});
				if(out_degree[v] == 0)
					adj[v].push_back({V-1, 0});
			}

		}

		double get_aec(int node){
			// Average execution time of a task(node)
			double num = 0;
			for(int i = 0; i < np; i++){
				num += (exec_time[i][node]);
			}
			return ((double)num)/np;
		}

		void generate_critical_paths(){
			int count = 0, n = V-2;
			while(n){				// while all tasks are not pushed to some critical path
				vector<double>L(V, 0);
				for(int v = 0; v < V; v++){
					for(auto x: adj[v]){
						int w = x.first, wt = x.second;
						double aec = get_aec(w);
						if(L[w] <= L[v]+aec+wt){
							L[w] 	= L[v]+aec+wt;
							prec[w] = v;
						}
					}
				}

				// Finding maximum execution time node (longest path)
				int loc = 0, maxL = 0;
				for(int v = 0; v < V; v++){
					if(maxL <= L[v]){
						maxL = L[v];
						loc  = v;
					}
				}

				// Building the path by backtraking using predecessors and adding the critical patht o the list
				list<int>cp;
				int node = loc;
				vector<bool>included(V, false);
				while(node != 0){
					node 			= prec[node];
					included[node] 	= true;
					done[node] 		= true;
					if(node>0 && node<V-1){
						cp.push_back(node);
						n--;
					}
				}
				// reversing to maintain topological order
				cp.reverse();
				CP.push_back(cp);

				// Make new graph by deleting picked up nodes of the critical paths (and edhes incedent on them)
				delete_nodes(included);

				// Added pseudo-nodes (Adding start and end pseudo nodes)
				add_pseudo_nodes();

			}
		}

		void calc_dependencies(bool print = false){
			// Calculating dependensies of each task from the grapgh
			for(int v = 1; v < V-1; v++){
				for(auto el: adj[v]){
					int w = el.first;
					if(w!=V-1)
					dpends[w].insert(v);
				}
			}
			if(print){
				printf("\n ============================== \n");
				printf(" DEPENDENCIES:\n");
				for(int v = 0; v < V; v++){
					printf(" %d: ", v);
					for(int x: dpends[v])
						printf(" %d ", x);
					cout << endl;
				}
			}
		}

		void util_predes(int node, int last = -1){
			// Depth first search and assign predesessors
			if(predes[node]==-1 || get_edge_weight(last, node) > get_edge_weight(predes[node], node))
				predes[node] = last;
			for(auto el: adj[node]){
				int w = el.first;
				util_predes(w, node);
			}
		}

		void calc_predes(bool print = false){
			// Calculating predesessors to each node
			util_predes(0);	// DFS of graph
			printf("\n ============================== \n");
			printf(" PREDECESSORS:\n  ");
			for(int x: predes) printf(" %d", x); cout << endl;
		}

		int get_next(list<int>ls){
			// Returns the next Ready task friom the list ls (also earses it before doing
			// Linked List is used for better delete efficiency (O(1))
			for(list<int>::iterator itr = ls.begin(); itr!=ls.end(); itr++){
				int x = *itr;
				if(!done[x] && dpends[x].size()==0){
					done[x] = true;
					ls.erase(itr);
					return x;
				}
			}
			return -1;
		}

		void update_dependencies(int node){
			// Updating dependencied after removal of node - node
			for(int v = 1; v < V-1; v++)
				dpends[v].erase(node);
		}

		void calc_que(){
			/*
				Calculating the Queues by parsing them and ading ready tasks to each queue
				Critical paths are traversed in a round robin way and at each visit all
				ready tasks (i.e nodes without any dependencies) are removed.
			*/
			done.clear(); done.resize(V, false);
			int j = 1;
			int n = CP.size(), v = V-2;
			for(int i = 0; v != 0; i++){
				vector<int>temp; i = i%n;
				while(true){
					int x = get_next(CP[i]);
					if(x == -1) break;
					temp.push_back(x); v--; // Reducing no. of nodes left of assign processor (keeping track to know when to stop)
					update_dependencies(x);
				}
				if(temp.size() != 0)
					qs.push_back(temp);
			}
		}

		int get_edge_weight(int n1, int n2){
			// Return edge weight between nodes n1->n2
			for(pair<int, int> v: adj_original[n1]){
				if(v.first == n2)
					return v.second;
			}
			return -1;
		}

		int get_min_index(vector<int>arr, bool print = false){
			// Extracting minimum Finish Time processor among all the processors
			printf("\n Processor End times: ");
			for(int x: arr) printf(" %d", x); cout << endl;
			int ind = -1, val = INT_MAX;
			for(int i = 0; i < arr.size(); i++){
				if(arr[i] < val){
					ind = i;
					val = arr[i];
				}
			}
			return ind;
		}

		void print_final_schedule(vector<int>SelectedProcessors){
			// Printing Final Results
			int count = 0;
			printf("\n ============================== \n");
			printf("  FINAL SCHEDULE TABLE (YAYYY!!)\n      ");
			for(int p = 0; p < np; p++) printf("  P%d", p+1); printf("   SelectedProcessor(Minimum End Time)\n");
			for(auto arr: FinalSchedule){
				printf("  Q%d: ", ++count);
				for(int x: arr)
					printf(" %3d", x);
				printf(" -> P%d\n", SelectedProcessors[count-1]);
			}

			printf("\n The least End Time processor is choosen for each Queue.");
			printf("\n ---------------------------- \n");
			printf(" Busy Schedule of each Processor\n");
			printf(" Processor {StartTime, EndTime}\n");

			for(int p = 0; p < np; p++){
				printf(" P%d: ", p+1);
				for(auto x: aval_time[p]){
					printf("{%d, %d}, ", x.first, x.second);
				}
				printf("\n");
			}
			printf("\n ============================== \n");
		}

		int get_earliest_availability(int p, int st, int et){
			// Find the earliest time the task (st-et) can be executed on processor - p
			int t = st;
			for(pair<int, int> el: aval_time[p]){
				int start = el.first, end = el.second;
				if(t+et < start) return t;
				t = end;
			}
			return t;
		}

		void schedule(){
			// Scheduling tasks
			/*
				For each queue we have to find the best processor to do it.
				So, for each queue
					-> We find the start and end time of the queue execution on every processor
					-> Get the processor with minimum finish time and assign it the queue (processor should be avilable)
					-> Note the busy time of the processor and finish time of each node (we will need 
									when we process its successor nodes who are dependent on a perticular node)

			*/

			// Calculate queues from the critical paths (Stored in Class Variable - qs)
			calc_que();
			print_q();
			printf("\n ============================== \n");
			printf(" SCHEDULING: \n");
			int n = qs.size();
			vector<int>pa(V, -1);
			vector<int>SelectedProcessors; 		// To note processor assigned to each queue
			vector<int>EndTime(V); EndTime[0] = 0;
			for(int j = 0; j < n; j++){
				printf(" Queue %d: \"START -> ", j+1);
				for(int w: qs[j]) printf("%d -> ", w); printf("END\"\n\n");
				vector<int>processor_time(np);
				vector<vector<int>>StartTime(np, vector<int>(V));
				vector<vector<int>>FinishTime(np, vector<int>(V));
				for(int p = 0; p < np; p++){
					/*	For each processor, find finish time of the queue
					*/
					int size = qs[j].size();
					printf(" Assigning Processor P%d: \n", p+1);
					for(int i = 0; i < size; i++){
						int w = qs[j][i];
						int pred = predes[w], M = 	(pa[pred]==-1||pa[pred]==p) ? 0 : get_edge_weight(pred, w); // M -> movement time from pred to node w (0 if both are from same processor)
						StartTime[p][w] 		= 	max(EndTime[pred]+M, get_earliest_availability(p, EndTime[pred]+M, exec_time[p][w])); 
						FinishTime[p][w] 		= 	StartTime[p][w]+exec_time[p][w];
						EndTime[w] 				= 	FinishTime[p][w];
						printf("    StartTime = %d | FinishTime = %d\n", StartTime[p][w], FinishTime[p][w]);
					}
				}
				/*	Pick the best processor among them (least finish time)
				*/
				for(int p = 0; p < np; p++){
					int end_time 		= 	*max_element(FinishTime[p].begin(), FinishTime[p].end());
					processor_time[p] 	= 	end_time;
				}
				FinalSchedule.push_back(processor_time);
				int best_processor 		= 	get_min_index(processor_time, true);
				for(int w: qs[j]){
					pa[w] 		= 	best_processor;
					EndTime[w] 	= 	FinishTime[best_processor][w];
				}
				// Start and end time of selected processor for this qeueue
				int cc_starttime 	= 	*max_element(StartTime[best_processor].begin(), StartTime[best_processor].end());
				int cc_endtime 		= 	*max_element(FinishTime[best_processor].begin(), FinishTime[best_processor].end());
				
				printf(" Selected Processor: P%d (%d)\n", best_processor+1, cc_endtime);
				SelectedProcessors.push_back(best_processor+1);
				// Noting when the processor will be busy
				aval_time[best_processor].push_back({cc_starttime, cc_endtime}); 
				sort(aval_time[best_processor].begin(), aval_time[best_processor].end());
				printf("---------------------------- \n");
			}
			print_final_schedule(SelectedProcessors);
		}

		void print_q(){
			/* Print the Calculated Queues
			*/
			printf("\n ============================== \n");
			int n = qs.size();
			printf(" No. of Queues: %d\n", n);
			printf(" QUEUES:\n");
			for(auto q: qs){
				printf(" \"START -> ");
				for(int w: q) printf("%d -> ", w); printf("END\"");
				cout << endl;
			}
		}

		void print_cps(){
			/* Print the Calculated Critical paths
			*/
			printf("\n ============================== \n");
			int n = CP.size();
			printf(" No. of Critical Paths: %d\n", n);
			printf(" CRITICAL PATHS\n");
			for(auto cp: CP){
				printf(" \"START -> ");
				for(int w: cp) printf("%d -> ", w); printf("END\"");
				cout << endl;
			}
		}

		void print_exec_time(){
			printf("\n ============================== \n");
			printf(" EXECUTION TIME OF TASKS(1-%d) for PROCCESSORS(1-%d):\n", V-2, np);
			printf("   N:"); for(int p = 0; p < np; p++) printf("  P%d", p+1); printf("\n");
			for(int n = 1; n < V-1; n++){
				printf(" %3d:", n);
				for(int p = 0; p < np; p++){
					printf(" %3d", exec_time[p][n]);
				}
				printf("\n");
			}
		}

		void print_adj(){
			printf("\n ============================== \n");
			printf(" GRAPH:\n");
			printf("   N: N1(w1) N1(w2) ...\n");
			for(int n1 = 0; n1 < V; n1++){
				printf("   %d: ", n1);
				for(auto x: adj[n1]){
					int n2 = x.first, w = x.second;
					printf("%d(%d)  ", n2, w);
				}
				printf("\n");
			}
		}
};



int main(){
	/*	Creating new object for executing CEFT algorithm and doing things the Mara way.
	*/
	CEFT g;
	g.print_adj();
	g.print_exec_time();
	g.calc_dependencies(true);
	g.calc_predes(true);
	g.generate_critical_paths();
	g.print_cps();
	g.schedule();
	cout << endl << endl;
}





